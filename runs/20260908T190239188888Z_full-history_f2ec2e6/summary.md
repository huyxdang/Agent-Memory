# LongMemEval five-question results

- Run ID: `20260908T190239188888Z_full-history_f2ec2e6`
- System: `full-history`
- Run status: `preflight_only`
- Retry of: `none`
- Dataset revision: `locomo`
- Dataset SHA-256: `see sources in manifest`
- Mem0 revision: `4b61c5d31b9c668a12b4f5e78064248a02c82d2b`
- Answer model requested: `gpt-5.6-luna`
- Judge model requested: `gpt-5`

## Local checks

| Check | Status | Detail |
|---|---|---|
| source_files_recorded | passed | locomo: 1 files hashed in metadata |
| selected_ids_unique | passed | question_ids_locomo_50.json: 50 questions |
| mem0_locomo_judge_prompts_exact | passed | 8ebac1ef60e9ab5caf99079fdaac038b85472e81491ed35e2d2655f3927c76c2 |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q82 | 20149 | 20225 | 1024 | 256 | 1050000 | 1028495 | True |
| locomo1_q2 | 15262 | 15340 | 1024 | 256 | 1050000 | 1033380 | True |
| locomo2_q65 | 29130 | 29206 | 1024 | 256 | 1050000 | 1019514 | True |
| locomo3_q88 | 25879 | 25955 | 1024 | 256 | 1050000 | 1022765 | True |
| locomo4_q71 | 29815 | 29897 | 1024 | 256 | 1050000 | 1018823 | True |
| locomo5_q61 | 29431 | 29507 | 1024 | 256 | 1050000 | 1019213 | True |
| locomo6_q67 | 27503 | 27578 | 1024 | 256 | 1050000 | 1021142 | True |
| locomo7_q15 | 27588 | 27662 | 1024 | 256 | 1050000 | 1021058 | True |
| locomo8_q83 | 21893 | 21974 | 1024 | 256 | 1050000 | 1026746 | True |
| locomo9_q71 | 27067 | 27144 | 1024 | 256 | 1050000 | 1021576 | True |
| locomo0_q83 | 20149 | 20225 | 1024 | 256 | 1050000 | 1028495 | True |
| locomo1_q4 | 15262 | 15339 | 1024 | 256 | 1050000 | 1033381 | True |
| locomo2_q66 | 29130 | 29210 | 1024 | 256 | 1050000 | 1019510 | True |
| locomo3_q89 | 25879 | 25955 | 1024 | 256 | 1050000 | 1022765 | True |
| locomo4_q72 | 29815 | 29893 | 1024 | 256 | 1050000 | 1018827 | True |
| locomo5_q62 | 29431 | 29512 | 1024 | 256 | 1050000 | 1019208 | True |
| locomo6_q68 | 27503 | 27583 | 1024 | 256 | 1050000 | 1021137 | True |
| locomo7_q16 | 27588 | 27665 | 1024 | 256 | 1050000 | 1021055 | True |
| locomo8_q84 | 21893 | 21968 | 1024 | 256 | 1050000 | 1026752 | True |
| locomo9_q72 | 27067 | 27150 | 1024 | 256 | 1050000 | 1021570 | True |
| locomo0_q0 | 20149 | 20226 | 1024 | 256 | 1050000 | 1028494 | True |
| locomo1_q0 | 15262 | 15339 | 1024 | 256 | 1050000 | 1033381 | True |
| locomo2_q0 | 29130 | 29212 | 1024 | 256 | 1050000 | 1019508 | True |
| locomo3_q2 | 25879 | 25961 | 1024 | 256 | 1050000 | 1022759 | True |
| locomo4_q6 | 29815 | 29896 | 1024 | 256 | 1050000 | 1018824 | True |
| locomo5_q0 | 29431 | 29510 | 1024 | 256 | 1050000 | 1019210 | True |
| locomo6_q1 | 27503 | 27585 | 1024 | 256 | 1050000 | 1021135 | True |
| locomo7_q0 | 27588 | 27673 | 1024 | 256 | 1050000 | 1021047 | True |
| locomo8_q4 | 21893 | 21972 | 1024 | 256 | 1050000 | 1026748 | True |
| locomo9_q0 | 27067 | 27142 | 1024 | 256 | 1050000 | 1021578 | True |
| locomo0_q1 | 20149 | 20223 | 1024 | 256 | 1050000 | 1028497 | True |
| locomo1_q1 | 15262 | 15339 | 1024 | 256 | 1050000 | 1033381 | True |
| locomo0_q3 | 20149 | 20221 | 1024 | 256 | 1050000 | 1028499 | True |
| locomo1_q3 | 15262 | 15339 | 1024 | 256 | 1050000 | 1033381 | True |
| locomo2_q2 | 29130 | 29204 | 1024 | 256 | 1050000 | 1019516 | True |
| locomo3_q1 | 25879 | 25956 | 1024 | 256 | 1050000 | 1022764 | True |
| locomo4_q0 | 29815 | 29893 | 1024 | 256 | 1050000 | 1018827 | True |
| locomo5_q2 | 29431 | 29510 | 1024 | 256 | 1050000 | 1019210 | True |
| locomo6_q2 | 27503 | 27583 | 1024 | 256 | 1050000 | 1021137 | True |
| locomo7_q1 | 27588 | 27666 | 1024 | 256 | 1050000 | 1021054 | True |
| locomo8_q0 | 21893 | 21968 | 1024 | 256 | 1050000 | 1026752 | True |
| locomo9_q1 | 27067 | 27145 | 1024 | 256 | 1050000 | 1021575 | True |
| locomo0_q4 | 20149 | 20222 | 1024 | 256 | 1050000 | 1028498 | True |
| locomo1_q5 | 15262 | 15340 | 1024 | 256 | 1050000 | 1033380 | True |
| locomo0_q2 | 20149 | 20229 | 1024 | 256 | 1050000 | 1028491 | True |
| locomo2_q8 | 29130 | 29204 | 1024 | 256 | 1050000 | 1019516 | True |
| locomo3_q0 | 25879 | 25956 | 1024 | 256 | 1050000 | 1022764 | True |
| locomo4_q3 | 29815 | 29897 | 1024 | 256 | 1050000 | 1018823 | True |
| locomo5_q19 | 29431 | 29514 | 1024 | 256 | 1050000 | 1019206 | True |
| locomo6_q0 | 27503 | 27577 | 1024 | 256 | 1050000 | 1021143 | True |

## Tracking summary

Fixed tokenizer: `o200k_base`. Output tokens include reasoning tokens; non-reasoning output is output minus reasoning.

| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Memory writing (not applicable) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Answering | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Judge (internal only) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |

- Reported system cost (judge excluded): `0.0`
- Total API spend (judge included): `0.0`

## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| locomo0_q82 | single-hop | What did the charity race raise awareness for? | mental health | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q2 | single-hop | How do Jon and Gina both like to destress? | by dancing | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q65 | single-hop | What is John's main focus in local politics? | Improving education and infrastructure | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q88 | single-hop | What is one of Joanna's favorite movies? | "Eternal Sunshineof the Spotless Mind" | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q71 | single-hop | Which team did John sign with on 21 May, 2023? | The Minnesota Wolves | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q61 | single-hop | Which specific type of bird mesmerizes Andrew? | Eagles | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q67 | single-hop | What programming languages has James worked with? | Python and C++ | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q15 | single-hop | What pets does Jolene have? | snakes | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q83 | single-hop | What type of car did Evan get after his old Prius broke down? | new Prius | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q71 | single-hop | How long did Calvin plan to stay in Japan? | A few months | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q83 | single-hop | What did Melanie realize after the charity race? | self-care is important | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q4 | single-hop | Why did Jon decide to start his dance studio? | He lost his job and decided to start his own business to share his passion. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q66 | single-hop | What sparked John's interest in improving education and infrastructure in the community? | Seeing how lack of education and crumbling infrastructure affected his neighborhood while growing up. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q89 | single-hop | What color did Nate choose for his hair? | purple | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q72 | single-hop | What is John's position on the team he signed with? | shooting guard | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q62 | single-hop | What did Andrew express missing about exploring nature trails with his family's dog? | The peaceful moments | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q68 | single-hop | What type of mobile application does James plan to build with John? | An app for dog walking and pet care | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q16 | single-hop | What are the names of Jolene's snakes? | Susie, Seraphim | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q84 | single-hop | How did Evan get into watercolor painting? | friend's advice | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q72 | single-hop | Which band was Dave's favorite at the music festival in April 2023? | Aerosmith | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q0 | temporal | When did Caroline go to the LGBTQ support group? | 7 May 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q0 | temporal | When Jon has lost his job as a banker? | 19 January, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q0 | temporal | Who did Maria have dinner with on May 3, 2023? | her mother | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q2 | temporal | When did Joanna first watch "Eternal Sunshine of the Spotless Mind? | 2019 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q6 | temporal | In which month's game did John achieve a career-high score in points? | June 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q0 | temporal | Which year did Audrey adopt the first three of her dogs? | 2020 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q1 | temporal | Which recreational activity was James pursuing on March 16, 2022? | bowling | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q0 | temporal | What kind of project was Jolene working on in the beginning of January 2023? | electricity engineering project | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q4 | temporal | Which hobby did Sam take up in May 2023? | painting | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q0 | temporal | When did Calvin first travel to Tokyo? | between 26 March and 20 April 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q1 | temporal | When did Melanie paint a sunrise? | 2022 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q1 | temporal | When Gina has lost her job at Door Dash? | January, 2023 | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q3 | multi-hop | What did Caroline research? | Adoption agencies | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q3 | multi-hop | What do Jon and Gina both have in common? | They lost their jobs and decided to start their own businesses. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q2 | multi-hop | What martial arts has John done? | Kickboxing, Taekwondo | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q1 | multi-hop | What kind of interests do Joanna and Nate share? | Watching movies, making desserts | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q0 | multi-hop | what are John's goals with regards to his basketball career? | improve shooting percentage, win a championship | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q2 | multi-hop | What kind of indoor activities has Andrew pursued with his girlfriend? | boardgames, volunteering at pet shelter, wine tasting, growing flowers | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q2 | multi-hop | Which places or events have John and James planned to meet at? | VR Club, McGee's, baseball game | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo7_q1 | multi-hop | Which of Deborah`s family and friends have passed away? | mother, father, her friend Karlie | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo8_q0 | multi-hop | What kind of car does Evan drive? | Prius | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo9_q1 | multi-hop | What items did Calvin buy in March 2023? | mansion in Japan, luxury car Ferrari 488 GTB | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q4 | multi-hop | What is Caroline's identity? | Transgender woman | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo1_q5 | multi-hop | What Jon thinks the ideal dance studio should look like? | By the water, with natural light and Marley flooring | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo0_q2 | open-domain | What fields would Caroline be likely to pursue in her educaton? | Psychology, counseling certification | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo2_q8 | open-domain | What might John's financial status be? | Middle-class or wealthy | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo3_q0 | open-domain | Is it likely that Nate has friends besides Joanna? | Yesteammates on hisvideo game team. | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo4_q3 | open-domain | Would Tim enjoy reading books by C. S. Lewis or John Greene? | C. S.Lewis | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo5_q19 | open-domain | What is an indoor activity that Andrew would enjoy doing while make his dog happy? | cook dog treats | NOT RUN | NOT RUN | NOT RUN | not_run |
| locomo6_q0 | open-domain | What are John's suspected health problems? | Obesity | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q61 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q62 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q16 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q19 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| locomo0_q82 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q65 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q88 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q61 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q67 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q15 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q71 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q83 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q66 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q89 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q62 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q68 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q16 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q84 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q72 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q6 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo7_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo8_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo9_q1 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q4 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo1_q5 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo0_q2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo2_q8 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo3_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo4_q3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo5_q19 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| locomo6_q0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': 'locomo0_q82', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q65', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q88', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q71', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q61', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q67', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q15', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q83', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q71', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q83', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q66', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q89', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q72', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q62', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q68', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q16', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q84', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q72', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q6', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo7_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo8_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo9_q1', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q4', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo1_q5', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo0_q2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo2_q8', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo3_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo4_q3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo5_q19', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'locomo6_q0', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `2.78443946`
- Reported system cost, excluding judge: `0.0`
- Internal judging cost: `0.0`
- Total API spend: `0.0`
