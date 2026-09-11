"""GPU inference only. No dataset selection, credentials or Modal dependency."""
import importlib.metadata
import json
import sys
import time

from modal_pilot_core import output_valid, prompt_ids, validate_payload


def emit(event):
    print('PILOT_EVENT '+json.dumps(event,ensure_ascii=False),flush=True)


def run(payload):
    validate_payload(payload)
    import torch
    from transformers import AutoModelForImageTextToText, AutoTokenizer
    started=time.monotonic()
    tokenizer=AutoTokenizer.from_pretrained(payload['model'],revision=payload['revision'])
    prepared=[]
    for row in payload['examples']:
        ids=prompt_ids(tokenizer,row['messages'])
        if len(ids)!=row['input_tokens'] or len(ids)+payload['max_output_tokens']>payload['context_window']:
            raise ValueError('GPU tokenizer disagrees with preflight; refusing truncation')
        prepared.append((row,ids))
    model=AutoModelForImageTextToText.from_pretrained(payload['model'],revision=payload['revision'],
        dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa').eval()
    emit({'event':'loaded','load_seconds':time.monotonic()-started,'gpu':torch.cuda.get_device_name(),
          'versions':{p:importlib.metadata.version(p) for p in ('torch','transformers','accelerate')},
          'precision':'bfloat16','thinking':False})
    for row,ids in prepared:
        start=time.monotonic()
        result={'event':'result','example_id':row['example_id'],'label':row['label'],
                'prompt_sha256':row['prompt_sha256'],'input_tokens':len(ids),'output_tokens':None,
                'reasoning_tokens':None,'status':'error','source_fidelity':'not_graded'}
        try:
            torch.cuda.reset_peak_memory_stats()
            inputs=torch.tensor([ids],device='cuda')
            torch.cuda.synchronize()
            with torch.inference_mode():
                generated=model.generate(input_ids=inputs,attention_mask=torch.ones_like(inputs),
                    max_new_tokens=payload['max_output_tokens'],do_sample=False,
                    pad_token_id=tokenizer.eos_token_id)
            torch.cuda.synchronize()
            output=generated[0,len(ids):].tolist()
            text=tokenizer.decode(output,skip_special_tokens=True)
            eos=model.generation_config.eos_token_id
            eos=eos if isinstance(eos,list) else [eos]
            finish='stop' if output and output[-1] in eos else 'length'
            result.update(output=text,output_tokens=len(output),finish_reason=finish,
                          valid_json=output_valid(text),gpu_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                          gpu_peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                          status='ok' if finish=='stop' and output_valid(text) else 'invalid_output')
        except Exception as error:
            result['error_type']=type(error).__name__
        result['inference_seconds']=time.monotonic()-start
        emit(result)
        if result['status']=='error':
            break


if __name__=='__main__':
    try:
        with open(sys.argv[1]) as stream:
            run(json.load(stream))
    except Exception as error:
        emit({'event':'fatal','error_type':type(error).__name__})
        raise SystemExit(1)
