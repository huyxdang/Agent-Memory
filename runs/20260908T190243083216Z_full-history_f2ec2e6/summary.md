# LongMemEval five-question results

- Run ID: `20260908T190243083216Z_full-history_f2ec2e6`
- System: `full-history`
- Run status: `preflight_only`
- Retry of: `none`
- Dataset revision: `beam`
- Dataset SHA-256: `see sources in manifest`
- Mem0 revision: `4b61c5d31b9c668a12b4f5e78064248a02c82d2b`
- Answer model requested: `gpt-5.6-luna`
- Judge model requested: `gpt-5`

## Local checks

| Check | Status | Detail |
|---|---|---|
| source_files_recorded | passed | beam: 16 files hashed in metadata |
| selected_ids_unique | passed | question_ids_beam_50.json: 50 questions |
| mem0_beam_judge_prompts_exact | passed | a1c2a4822898411f90ab2915a72d2b2031f97437bdcc1b3ac2008fe93653267b |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| beam100K_1_abstention_0 | 131065 | 131143 | 1024 | 256 | 1050000 | 917577 | True |
| beam100K_1_contradiction_resolution_0 | 131065 | 131139 | 1024 | 256 | 1050000 | 917581 | True |
| beam100K_1_event_ordering_0 | 131065 | 131157 | 1024 | 256 | 1050000 | 917563 | True |
| beam100K_1_information_extraction_0 | 131065 | 131132 | 1024 | 256 | 1050000 | 917588 | True |
| beam100K_1_instruction_following_0 | 131065 | 131136 | 1024 | 256 | 1050000 | 917584 | True |
| beam100K_1_knowledge_update_0 | 131065 | 131136 | 1024 | 256 | 1050000 | 917584 | True |
| beam100K_1_multi_session_reasoning_0 | 131065 | 131142 | 1024 | 256 | 1050000 | 917578 | True |
| beam100K_1_preference_following_0 | 131065 | 131160 | 1024 | 256 | 1050000 | 917560 | True |
| beam100K_1_summarization_0 | 131065 | 131157 | 1024 | 256 | 1050000 | 917563 | True |
| beam100K_1_temporal_reasoning_0 | 131065 | 131143 | 1024 | 256 | 1050000 | 917577 | True |
| beam100K_4_abstention_0 | 111974 | 112051 | 1024 | 256 | 1050000 | 936669 | True |
| beam100K_4_contradiction_resolution_0 | 111974 | 112044 | 1024 | 256 | 1050000 | 936676 | True |
| beam100K_4_event_ordering_0 | 111974 | 112097 | 1024 | 256 | 1050000 | 936623 | True |
| beam100K_4_information_extraction_0 | 111974 | 112066 | 1024 | 256 | 1050000 | 936654 | True |
| beam100K_4_instruction_following_0 | 111974 | 112050 | 1024 | 256 | 1050000 | 936670 | True |
| beam100K_4_knowledge_update_0 | 111974 | 112050 | 1024 | 256 | 1050000 | 936670 | True |
| beam100K_4_multi_session_reasoning_0 | 111974 | 112053 | 1024 | 256 | 1050000 | 936667 | True |
| beam100K_4_preference_following_0 | 111974 | 112060 | 1024 | 256 | 1050000 | 936660 | True |
| beam100K_4_summarization_0 | 111974 | 112063 | 1024 | 256 | 1050000 | 936657 | True |
| beam100K_4_temporal_reasoning_0 | 111974 | 112080 | 1024 | 256 | 1050000 | 936640 | True |
| beam100K_6_abstention_0 | 127055 | 127133 | 1024 | 256 | 1050000 | 921587 | True |
| beam100K_6_contradiction_resolution_0 | 127055 | 127129 | 1024 | 256 | 1050000 | 921591 | True |
| beam100K_6_event_ordering_0 | 127055 | 127147 | 1024 | 256 | 1050000 | 921573 | True |
| beam100K_6_information_extraction_0 | 127055 | 127133 | 1024 | 256 | 1050000 | 921587 | True |
| beam100K_6_instruction_following_0 | 127055 | 127126 | 1024 | 256 | 1050000 | 921594 | True |
| beam100K_6_knowledge_update_0 | 127055 | 127130 | 1024 | 256 | 1050000 | 921590 | True |
| beam100K_6_multi_session_reasoning_0 | 127055 | 127140 | 1024 | 256 | 1050000 | 921580 | True |
| beam100K_6_preference_following_0 | 127055 | 127136 | 1024 | 256 | 1050000 | 921584 | True |
| beam100K_6_summarization_0 | 127055 | 127136 | 1024 | 256 | 1050000 | 921584 | True |
| beam100K_6_temporal_reasoning_0 | 127055 | 127152 | 1024 | 256 | 1050000 | 921568 | True |
| beam100K_13_abstention_0 | 120997 | 121083 | 1024 | 256 | 1050000 | 927637 | True |
| beam100K_13_contradiction_resolution_0 | 120997 | 121070 | 1024 | 256 | 1050000 | 927650 | True |
| beam100K_13_event_ordering_0 | 120997 | 121087 | 1024 | 256 | 1050000 | 927633 | True |
| beam100K_13_information_extraction_0 | 120997 | 121077 | 1024 | 256 | 1050000 | 927643 | True |
| beam100K_13_instruction_following_0 | 120997 | 121070 | 1024 | 256 | 1050000 | 927650 | True |
| beam100K_13_knowledge_update_0 | 120997 | 121071 | 1024 | 256 | 1050000 | 927649 | True |
| beam100K_13_multi_session_reasoning_0 | 120997 | 121074 | 1024 | 256 | 1050000 | 927646 | True |
| beam100K_13_preference_following_0 | 120997 | 121081 | 1024 | 256 | 1050000 | 927639 | True |
| beam100K_13_summarization_0 | 120997 | 121075 | 1024 | 256 | 1050000 | 927645 | True |
| beam100K_13_temporal_reasoning_0 | 120997 | 121074 | 1024 | 256 | 1050000 | 927646 | True |
| beam100K_16_abstention_0 | 145041 | 145121 | 1024 | 256 | 1050000 | 903599 | True |
| beam100K_16_contradiction_resolution_0 | 145041 | 145112 | 1024 | 256 | 1050000 | 903608 | True |
| beam100K_16_event_ordering_0 | 145041 | 145131 | 1024 | 256 | 1050000 | 903589 | True |
| beam100K_16_information_extraction_0 | 145041 | 145118 | 1024 | 256 | 1050000 | 903602 | True |
| beam100K_16_instruction_following_0 | 145041 | 145113 | 1024 | 256 | 1050000 | 903607 | True |
| beam100K_16_knowledge_update_0 | 145041 | 145114 | 1024 | 256 | 1050000 | 903606 | True |
| beam100K_16_multi_session_reasoning_0 | 145041 | 145123 | 1024 | 256 | 1050000 | 903597 | True |
| beam100K_16_preference_following_0 | 145041 | 145135 | 1024 | 256 | 1050000 | 903585 | True |
| beam100K_16_summarization_0 | 145041 | 145117 | 1024 | 256 | 1050000 | 903603 | True |
| beam100K_16_temporal_reasoning_0 | 145041 | 145120 | 1024 | 256 | 1050000 | 903600 | True |

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
| beam100K_1_abstention_0 | abstention | How did the user feedback influence the UI/UX improvements I made before the public launch? | Based on the provided chat, there is no information related to how user feedback influenced UI/UX improvements. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_contradiction_resolution_0 | contradiction_resolution | Have I worked with Flask routes and handled HTTP requests in this project? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of developing my personal budget tracker throughout our conversations, in order? Mention ONLY and ONLY three items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_information_extraction_0 | information_extraction | When does my first sprint end? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_instruction_following_0 | instruction_following | Could you show me how to implement a login feature? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_knowledge_update_0 | knowledge_update | What is the average response time of the dashboard API? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_multi_session_reasoning_0 | multi_session_reasoning | How many new columns did I want to add to the transactions table across my requests? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_preference_following_0 | preference_following | I'm planning to add user login, income and expense tracking, and some basic analytics to my Flask app. What libraries or tools would you suggest I use to implement these features? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_summarization_0 | summarization | Can you provide a comprehensive summary of how my budget tracker project has progressed, including the key features implemented, the development timeline, security enhancements, and documentation efforts? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_1_temporal_reasoning_0 | temporal_reasoning | How many weeks do I have between finishing the transaction management features and the final deployment deadline? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_abstention_0 | abstention | What specific criteria did I consider when choosing between angle-based or side-based classification strategies? | Based on the provided chat, there is no information related to the specific criteria considered for choosing classification strategies. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_contradiction_resolution_0 | contradiction_resolution | Have I ever worked on triangle classification problems before? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of classifying triangles throughout our conversations, including how I first approached understanding their types, then moved on to calculating areas, identifying key characteristics, comparing types, and finally applying these concepts to more complex problems, in order? Mention ONLY and ONLY nine items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_information_extraction_0 | information_extraction | What approach did I outline to demonstrate that two triangles with matching angle pairs and a connecting segment are identical, and how did I organize the information to support this? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_instruction_following_0 | instruction_following | How can I find the area of a triangle using medians and altitudes? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_knowledge_update_0 | knowledge_update | What is my accuracy percentage in solving area calculation problems after completing 15 problems? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_multi_session_reasoning_0 | multi_session_reasoning | How many triangle classification problems have I completed in total across all sessions where I mentioned my progress? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_preference_following_0 | preference_following | Can you show me how to calculate the area of this triangle using different methods and also help me find the length of the median? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_summarization_0 | summarization | Can you give me a clear summary of everything we've covered about triangles, including how to verify right angles, calculate areas, and understand medians? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_4_temporal_reasoning_0 | temporal_reasoning | Which improvement happened first: my quiz score increasing from 65% to 82% after focusing on triangle side classifications, or my test score rising from 80% to 92% on congruence proofs and similarity calculations? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_abstention_0 | abstention | What specific advice did Bryan give about updating the LinkedIn profile in April 2024? | Based on the provided chat, there is no information related to the specific advice Bryan gave about updating the LinkedIn profile. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_contradiction_resolution_0 | contradiction_resolution | Have I ever enrolled in any courses or training programs on ATS optimization? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of improving my professional profile and resume throughout our conversations in order? Mention ONLY and ONLY six items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_information_extraction_0 | information_extraction | How much does my subscription to the service I’m using for my resume cost each month? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_instruction_following_0 | instruction_following | How should I organize the information about my past jobs? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_knowledge_update_0 | knowledge_update | How many interviews have I secured for executive producer roles during the recent period? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_multi_session_reasoning_0 | multi_session_reasoning | How many different areas have I focused on updating or improving based on my messages about my resume, portfolio, and salary negotiation? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_preference_following_0 | preference_following | I'm updating my portfolio and want to include some samples. What types of content would you suggest I add? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_summarization_0 | summarization | Can you give me a summary of how I worked on improving my resume and job application strategy over time? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_6_temporal_reasoning_0 | temporal_reasoning | How many days do I have between the deadline to tailor my resume for film, television, and digital media and the date I want to be ready to apply confidently for executive producer roles? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_abstention_0 | abstention | What was the atmosphere like during the February 20 book club discussion on 'The Poppy War' hosted by Kelly and I? | Based on the provided chat, there is no information related to the atmosphere during the February 20 book club discussion on 'The Poppy War'. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_contradiction_resolution_0 | contradiction_resolution | Have I ever met Kelly at any book club or library event? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_event_ordering_0 | event_ordering | Can you list the order in which I brought up different aspects of my book club activities throughout our conversations in order? Mention ONLY and ONLY five items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_information_extraction_0 | information_extraction | How many series did I say were on my reading list, and what was the total page count? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_instruction_following_0 | instruction_following | Can you suggest some good audiobooks for me to listen to? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_knowledge_update_0 | knowledge_update | How many books am I aiming to read in my winter reading challenge? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_multi_session_reasoning_0 | multi_session_reasoning | How many different book series or genres have I mentioned wanting to explore across my conversations? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_preference_following_0 | preference_following | I'm looking to add some new books to my collection and also want something easy to carry around. What would you suggest? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_summarization_0 | summarization | Can you summarize how my reading goals and strategies have developed over time based on our conversations? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_13_temporal_reasoning_0 | temporal_reasoning | How many days did it take me to finish reading the trilogy after I downloaded it? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_abstention_0 | abstention | What are Alexis’s specific plans and strategies for launching the freelance design business in January 2025? | Based on the provided chat, there is no information related to Alexis’s specific plans or strategies for launching the freelance design business. | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_contradiction_resolution_0 | contradiction_resolution | Have U been using Excel to track my daily expenses? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_event_ordering_0 | event_ordering | Can you walk me through the order in which I brought up different financial planning topics during our chats, in order? Mention ONLY and ONLY four items. |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_information_extraction_0 | information_extraction | What monthly amount did I say I’m currently paying for my place on Bay Street? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_instruction_following_0 | instruction_following | How much am I allowed to spend on my holiday plans? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_knowledge_update_0 | knowledge_update | What is the monthly grocery budget Alexis and I have agreed on? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_multi_session_reasoning_0 | multi_session_reasoning | How much money had I saved in total by the time I reached 60% of my emergency fund goal? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_preference_following_0 | preference_following | I want to set up a system to track my monthly expenses and stick to a dining out budget of $200 starting next month. How would you suggest I organize this? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_summarization_0 | summarization | Can you summarize how my approach to managing finances with Alexis has developed over time? |  | NOT RUN | NOT RUN | NOT RUN | not_run |
| beam100K_16_temporal_reasoning_0 | temporal_reasoning | How many days had I been tracking my daily expenses before I felt frustrated enough to consider stopping? |  | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| beam100K_1_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| beam100K_1_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_1_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_4_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_6_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_13_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_abstention_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_contradiction_resolution_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_event_ordering_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_information_extraction_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_instruction_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_knowledge_update_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_multi_session_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_preference_following_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_summarization_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| beam100K_16_temporal_reasoning_0 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': 'beam100K_1_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_1_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_4_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_6_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_13_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_abstention_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_contradiction_resolution_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_event_ordering_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_information_extraction_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_instruction_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_knowledge_update_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_multi_session_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_preference_following_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_summarization_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'beam100K_16_temporal_reasoning_0', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `3.82816915`
- Reported system cost, excluding judge: `0.0`
- Internal judging cost: `0.0`
- Total API spend: `0.0`
