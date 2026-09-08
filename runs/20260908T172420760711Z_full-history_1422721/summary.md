# LongMemEval five-question results

- Run ID: `20260908T172420760711Z_full-history_1422721`
- System: `full-history`
- Run status: `preflight_only`
- Retry of: `none`
- Dataset revision: `98d7416c24c778c2fee6e6f3006e7a073259d48f`
- Dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- Mem0 revision: `4b61c5d31b9c668a12b4f5e78064248a02c82d2b`
- Answer model requested: `gpt-5.6-luna`
- Judge model requested: `gpt-5`

## Local checks

| Check | Status | Detail |
|---|---|---|
| dataset_sha256 | passed | d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442 |
| dataset_500_unique_questions | passed | validated while loading |
| selected_ids_unique | passed | question_ids_50.json: 50 questions |
| complete_history_and_no_labels | passed | validated while building every prompt |
| mem0_judge_prompt_exact_text | passed | c4dc2f6e34e92f9958b62222a0ed520b3ce80dede68bba164dc7961c27dae515 |
| mem0_yes_no_parser_cases | passed | yes, no, last-token, empty, and garbage cases |
| all_answer_prompts_fit | passed | configured context window |

## Prompt fit

| ID | History context tokens | Complete prompt tokens | Maximum answer | Margin | Context window | Remaining | Fits |
|---|---:|---:|---:|---:|---:|---:|---|
| e47becba | 110325 | 110400 | 1024 | 256 | 1050000 | 938320 | True |
| 118b2229 | 108598 | 108675 | 1024 | 256 | 1050000 | 940045 | True |
| 51a45a95 | 111144 | 111225 | 1024 | 256 | 1050000 | 937495 | True |
| 58bf7951 | 111305 | 111384 | 1024 | 256 | 1050000 | 937336 | True |
| 1e043500 | 110878 | 110958 | 1024 | 256 | 1050000 | 937762 | True |
| c5e8278d | 111322 | 111400 | 1024 | 256 | 1050000 | 937320 | True |
| 6ade9755 | 109589 | 109664 | 1024 | 256 | 1050000 | 939056 | True |
| 6f9b354f | 112015 | 112092 | 1024 | 256 | 1050000 | 936628 | True |
| 7161e7e2 | 109655 | 109754 | 1024 | 256 | 1050000 | 938966 | True |
| c4f10528 | 111105 | 111209 | 1024 | 256 | 1050000 | 937511 | True |
| 89527b6b | 111532 | 111635 | 1024 | 256 | 1050000 | 937085 | True |
| e9327a54 | 109775 | 109874 | 1024 | 256 | 1050000 | 938846 | True |
| 4c36ccef | 111327 | 111414 | 1024 | 256 | 1050000 | 937306 | True |
| 6ae235be | 109879 | 109982 | 1024 | 256 | 1050000 | 938738 | True |
| 7e00a6cb | 109851 | 109949 | 1024 | 256 | 1050000 | 938771 | True |
| 1903aded | 109410 | 109507 | 1024 | 256 | 1050000 | 939213 | True |
| 8a2466db | 111417 | 111499 | 1024 | 256 | 1050000 | 937221 | True |
| 06878be2 | 110896 | 110977 | 1024 | 256 | 1050000 | 937743 | True |
| 75832dbd | 108500 | 108582 | 1024 | 256 | 1050000 | 940138 | True |
| 0edc2aef | 111842 | 111922 | 1024 | 256 | 1050000 | 936798 | True |
| 35a27287 | 107642 | 107723 | 1024 | 256 | 1050000 | 940997 | True |
| 32260d93 | 109505 | 109586 | 1024 | 256 | 1050000 | 939134 | True |
| 195a1a1b | 110089 | 110170 | 1024 | 256 | 1050000 | 938550 | True |
| afdc33df | 112225 | 112311 | 1024 | 256 | 1050000 | 936409 | True |
| caf03d32 | 111023 | 111107 | 1024 | 256 | 1050000 | 937613 | True |
| 0a995998 | 111429 | 111514 | 1024 | 256 | 1050000 | 937206 | True |
| 6d550036 | 104748 | 104827 | 1024 | 256 | 1050000 | 943893 | True |
| gpt4_59c863d7 | 110665 | 110744 | 1024 | 256 | 1050000 | 937976 | True |
| b5ef892d | 110408 | 110492 | 1024 | 256 | 1050000 | 938228 | True |
| e831120c | 110016 | 110107 | 1024 | 256 | 1050000 | 938613 | True |
| 3a704032 | 111548 | 111627 | 1024 | 256 | 1050000 | 937093 | True |
| gpt4_d84a3211 | 109901 | 109987 | 1024 | 256 | 1050000 | 938733 | True |
| aae3761f | 109097 | 109182 | 1024 | 256 | 1050000 | 939538 | True |
| gpt4_59149c77 | 108763 | 108864 | 1024 | 256 | 1050000 | 939856 | True |
| gpt4_f49edff3 | 109737 | 109855 | 1024 | 256 | 1050000 | 938865 | True |
| 71017276 | 109705 | 109790 | 1024 | 256 | 1050000 | 938930 | True |
| b46e15ed | 111723 | 111811 | 1024 | 256 | 1050000 | 936909 | True |
| gpt4_fa19884c | 107909 | 108006 | 1024 | 256 | 1050000 | 940714 | True |
| 0bc8ad92 | 108916 | 108999 | 1024 | 256 | 1050000 | 939721 | True |
| af082822 | 111283 | 111367 | 1024 | 256 | 1050000 | 937353 | True |
| gpt4_4929293a | 111200 | 111283 | 1024 | 256 | 1050000 | 937437 | True |
| 6a1eabeb | 109643 | 109725 | 1024 | 256 | 1050000 | 938995 | True |
| 6aeb4375 | 108013 | 108092 | 1024 | 256 | 1050000 | 940628 | True |
| 830ce83f | 109372 | 109450 | 1024 | 256 | 1050000 | 939270 | True |
| 852ce960 | 109372 | 109458 | 1024 | 256 | 1050000 | 939262 | True |
| 945e3d21 | 111714 | 111795 | 1024 | 256 | 1050000 | 936925 | True |
| d7c942c3 | 111303 | 111383 | 1024 | 256 | 1050000 | 937337 | True |
| 71315a70 | 111108 | 111188 | 1024 | 256 | 1050000 | 937532 | True |
| 89941a93 | 111209 | 111285 | 1024 | 256 | 1050000 | 937435 | True |
| ce6d2d27 | 110484 | 110565 | 1024 | 256 | 1050000 | 938155 | True |

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
| e47becba | single-session-user | What degree did I graduate with? | Business Administration | NOT RUN | NOT RUN | NOT RUN | not_run |
| 118b2229 | single-session-user | How long is my daily commute to work? | 45 minutes each way | NOT RUN | NOT RUN | NOT RUN | not_run |
| 51a45a95 | single-session-user | Where did I redeem a $5 coupon on coffee creamer? | Target | NOT RUN | NOT RUN | NOT RUN | not_run |
| 58bf7951 | single-session-user | What play did I attend at the local community theater? | The Glass Menagerie | NOT RUN | NOT RUN | NOT RUN | not_run |
| 1e043500 | single-session-user | What is the name of the playlist I created on Spotify? | Summer Vibes | NOT RUN | NOT RUN | NOT RUN | not_run |
| c5e8278d | single-session-user | What was my last name before I changed it? | Johnson | NOT RUN | NOT RUN | NOT RUN | not_run |
| 6ade9755 | single-session-user | Where do I take yoga classes? | Serenity Yoga | NOT RUN | NOT RUN | NOT RUN | not_run |
| 6f9b354f | single-session-user | What color did I repaint my bedroom walls? | a lighter shade of gray | NOT RUN | NOT RUN | NOT RUN | not_run |
| 7161e7e2 | single-session-assistant | I'm checking our previous chat about the shift rotation sheet for GM social media agents. Can you remind me what was the rotation for Admon on a Sunday? | Admon was assigned to the 8 am - 4 pm (Day Shift) on Sundays. | NOT RUN | NOT RUN | NOT RUN | not_run |
| c4f10528 | single-session-assistant | I'm planning to visit Bandung again and I was wondering if you could remind me of the name of that restaurant in Cihampelas Walk that serves a great Nasi Goreng? | Miss Bee Providore | NOT RUN | NOT RUN | NOT RUN | not_run |
| 89527b6b | single-session-assistant | I'm going back to our previous conversation about the children's book on dinosaurs. Can you remind me what color was the scaly body of the Plesiosaur in the image? | The Plesiosaur had a blue scaly body. | NOT RUN | NOT RUN | NOT RUN | not_run |
| e9327a54 | single-session-assistant | I'm planning to revisit Orlando. I was wondering if you could remind me of that unique dessert shop with the giant milkshakes we talked about last time? | The Sugar Factory at Icon Park. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 4c36ccef | single-session-assistant | Can you remind me of the name of the romantic Italian restaurant in Rome you recommended for dinner? | Roscioli | NOT RUN | NOT RUN | NOT RUN | not_run |
| 6ae235be | single-session-assistant | I remember you told me about the refining processes at CITGO's three refineries earlier. Can you remind me what kind of processes are used at the Lake Charles Refinery? | Atmospheric distillation, fluid catalytic cracking (FCC), alkylation, and hydrotreating. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 7e00a6cb | single-session-assistant | I'm planning my trip to Amsterdam again and I was wondering, what was the name of that hostel near the Red Light District that you recommended last time? | International Budget Hostel | NOT RUN | NOT RUN | NOT RUN | not_run |
| 1903aded | single-session-assistant | I think we discussed work from home jobs for seniors earlier. Can you remind me what was the 7th job in the list you provided? | Transcriptionist. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 8a2466db | single-session-preference | Can you recommend some resources where I can learn more about video editing? | The user would prefer responses that suggest resources specifically tailored to Adobe Premiere Pro, especially those that delve into its advanced settings. They might not prefer general video editing resources or resources related to other video editing software. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 06878be2 | single-session-preference | Can you suggest some accessories that would complement my current photography setup? | The user would prefer suggestions of Sony-compatible accessories or high-quality photography gear that can enhance their photography experience. They may not prefer suggestions of other brands' equipment or low-quality gear. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 75832dbd | single-session-preference | Can you recommend some recent publications or conferences that I might find interesting? | The user would prefer suggestions related to recent research papers, articles, or conferences that focus on artificial intelligence in healthcare, particularly those that involve deep learning for medical image analysis. They would not be interested in general AI topics or those unrelated to healthcare. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 0edc2aef | single-session-preference | Can you suggest a hotel for my upcoming trip to Miami? | The user would prefer suggestions of hotels in Miami that offer great views, possibly of the ocean or the city skyline, and have unique features such as a rooftop pool or a hot tub on the balcony. They may not prefer suggestions of basic or budget hotels without these features. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 35a27287 | single-session-preference | Can you recommend some interesting cultural events happening around me this weekend? | The user would prefer responses that suggest cultural events where they can practice their language skills, particularly Spanish and French. They would also appreciate if the event has a focus on language learning resources. They would not prefer events that do not provide opportunities for language practice or cultural exchange. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 32260d93 | single-session-preference | Can you recommend a show or movie for me to watch tonight? | The user would prefer recommendations for stand-up comedy specials on Netflix, especially those that are known for their storytelling. They may not prefer recommendations for other genres or platforms. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 195a1a1b | single-session-preference | Can you suggest some activities that I can do in the evening? | The user would prefer suggestions that involve relaxing activities that can be done in the evening, preferably before 9:30 pm. They would not prefer suggestions that involve using their phone or watching TV, as these activities have been affecting their sleep quality. | NOT RUN | NOT RUN | NOT RUN | not_run |
| afdc33df | single-session-preference | My kitchen's becoming a bit of a mess again. Any tips for keeping it clean? | The user would prefer responses that acknowledge and build upon their existing efforts to organize their kitchen, such as utilizing their new utensil holder to keep countertops clutter-free. They would also appreciate tips that address their concern for maintaining their granite surface, particularly around the sink area. Preferred responses would provide practical and actionable steps to maintain cleanliness, leveraging the user's current tools and setup. They might not prefer generic or vague suggestions that do not take into account their specific kitchen setup or concerns. | NOT RUN | NOT RUN | NOT RUN | not_run |
| caf03d32 | single-session-preference | I've been struggling with my slow cooker recipes. Any advice on getting better results? | The user would prefer responses that provide tips and advice specifically tailored to their slow cooker experiences, utilizing their recent success with beef stew and interest in making yogurt in the slow cooker. They might not prefer general slow cooker recipes or advice unrelated to their specific experiences and interests. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 0a995998 | multi-session | How many items of clothing do I need to pick up or return from a store? | 3 | NOT RUN | NOT RUN | NOT RUN | not_run |
| 6d550036 | multi-session | How many projects have I led or am currently leading? | 2 | NOT RUN | NOT RUN | NOT RUN | not_run |
| gpt4_59c863d7 | multi-session | How many model kits have I worked on or bought? | I have worked on or bought five model kits. The scales of the models are: Revell F-15 Eagle (scale not mentioned), Tamiya 1/48 scale Spitfire Mk.V, 1/16 scale German Tiger I tank, 1/72 scale B-29 bomber, and 1/24 scale '69 Camaro. | NOT RUN | NOT RUN | NOT RUN | not_run |
| b5ef892d | multi-session | How many days did I spend on camping trips in the United States this year? | 8 days. | NOT RUN | NOT RUN | NOT RUN | not_run |
| e831120c | multi-session | How many weeks did it take me to watch all the Marvel Cinematic Universe movies and the main Star Wars films? | 3.5 weeks | NOT RUN | NOT RUN | NOT RUN | not_run |
| 3a704032 | multi-session | How many plants did I acquire in the last month? | 3 | NOT RUN | NOT RUN | NOT RUN | not_run |
| gpt4_d84a3211 | multi-session | How much total money have I spent on bike-related expenses since the start of the year? | $185 | NOT RUN | NOT RUN | NOT RUN | not_run |
| aae3761f | multi-session | How many hours in total did I spend driving to my three road trip destinations combined? | 15 hours for getting to the three destinations (or 30 hours for the round trip) | NOT RUN | NOT RUN | NOT RUN | not_run |
| gpt4_59149c77 | temporal-reasoning | How many days passed between my visit to the Museum of Modern Art (MoMA) and the 'Ancient Civilizations' exhibit at the Metropolitan Museum of Art? | 7 days. 8 days (including the last day) is also acceptable. | NOT RUN | NOT RUN | NOT RUN | not_run |
| gpt4_f49edff3 | temporal-reasoning | Which three events happened in the order from first to last: the day I helped my friend prepare the nursery, the day I helped my cousin pick out stuff for her baby shower, and the day I ordered a customized phone case for my friend's birthday? | First, I helped my friend prepare the nursery, then I helped my cousin pick out stuff for her baby shower, and lastly, I ordered a customized phone case for my friend's birthday. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 71017276 | temporal-reasoning | How many weeks ago did I meet up with my aunt and receive the crystal chandelier? | 4 | NOT RUN | NOT RUN | NOT RUN | not_run |
| b46e15ed | temporal-reasoning | How many months have passed since I participated in two charity events in a row, on consecutive days? | 2 | NOT RUN | NOT RUN | NOT RUN | not_run |
| gpt4_fa19884c | temporal-reasoning | How many days passed between the day I started playing along to my favorite songs on my old keyboard and the day I discovered a bluegrass band? | 6 days. 7 days (including the last day) is also acceptable. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 0bc8ad92 | temporal-reasoning | How many months have passed since I last visited a museum with a friend? | 5 | NOT RUN | NOT RUN | NOT RUN | not_run |
| af082822 | temporal-reasoning | How many weeks ago did I attend the friends and family sale at Nordstrom? | 2 | NOT RUN | NOT RUN | NOT RUN | not_run |
| gpt4_4929293a | temporal-reasoning | Which event happened first, my cousin's wedding or Michael's engagement party? | Michael's engagement party | NOT RUN | NOT RUN | NOT RUN | not_run |
| 6a1eabeb | knowledge-update | What was my personal best time in the charity 5K run? | 25 minutes and 50 seconds (or 25:50) | NOT RUN | NOT RUN | NOT RUN | not_run |
| 6aeb4375 | knowledge-update | How many Korean restaurants have I tried in my city? | four | NOT RUN | NOT RUN | NOT RUN | not_run |
| 830ce83f | knowledge-update | Where did Rachel move to after her recent relocation? | the suburbs | NOT RUN | NOT RUN | NOT RUN | not_run |
| 852ce960 | knowledge-update | What was the amount I was pre-approved for when I got my mortgage from Wells Fargo? | $400,000 | NOT RUN | NOT RUN | NOT RUN | not_run |
| 945e3d21 | knowledge-update | How often do I attend yoga classes to help with my anxiety? | Three times a week. | NOT RUN | NOT RUN | NOT RUN | not_run |
| d7c942c3 | knowledge-update | Is my mom using the same grocery list method as me? | Yes. | NOT RUN | NOT RUN | NOT RUN | not_run |
| 71315a70 | knowledge-update | How many hours have I spent on my abstract ocean sculpture? | 10-12 hours | NOT RUN | NOT RUN | NOT RUN | not_run |
| 89941a93 | knowledge-update | How many bikes do I currently own? | 4 | NOT RUN | NOT RUN | NOT RUN | not_run |
| ce6d2d27 | knowledge-update | What day of the week do I take a cocktail-making class? | Friday | NOT RUN | NOT RUN | NOT RUN | not_run |

## Answering usage

| ID | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| e47becba | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 118b2229 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 51a45a95 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 58bf7951 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 1e043500 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| c5e8278d | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6ade9755 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6f9b354f | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 7161e7e2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| c4f10528 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 89527b6b | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| e9327a54 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 4c36ccef | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6ae235be | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 7e00a6cb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 1903aded | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 8a2466db | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 06878be2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 75832dbd | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0edc2aef | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 35a27287 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 32260d93 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 195a1a1b | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| afdc33df | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| caf03d32 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0a995998 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6d550036 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_59c863d7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| b5ef892d | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| e831120c | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 3a704032 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_d84a3211 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| aae3761f | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_59149c77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_f49edff3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 71017276 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| b46e15ed | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_fa19884c | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0bc8ad92 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| af082822 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_4929293a | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6a1eabeb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6aeb4375 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 830ce83f | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 852ce960 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 945e3d21 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| d7c942c3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 71315a70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 89941a93 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| ce6d2d27 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judging usage

| Item | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds | Resolved model |
|---|---:|---:|---:|---:|---:|---:|---|
| e47becba | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 118b2229 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 51a45a95 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 58bf7951 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 1e043500 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| c5e8278d | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6ade9755 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6f9b354f | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 7161e7e2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| c4f10528 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 89527b6b | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| e9327a54 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 4c36ccef | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6ae235be | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 7e00a6cb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 1903aded | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 8a2466db | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 06878be2 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 75832dbd | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0edc2aef | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 35a27287 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 32260d93 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 195a1a1b | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| afdc33df | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| caf03d32 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0a995998 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6d550036 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_59c863d7 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| b5ef892d | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| e831120c | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 3a704032 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_d84a3211 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| aae3761f | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_59149c77 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_f49edff3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 71017276 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| b46e15ed | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_fa19884c | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 0bc8ad92 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| af082822 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| gpt4_4929293a | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6a1eabeb | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 6aeb4375 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 830ce83f | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 852ce960 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 945e3d21 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| d7c942c3 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 71315a70 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| 89941a93 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| ce6d2d27 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:e47becba:known_correct | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:e47becba:correct_paraphrase | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:e47becba:clearly_wrong | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:6a1eabeb:known_correct | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:6a1eabeb:correct_paraphrase | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| validation:6a1eabeb:clearly_wrong | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|
| e47becba:known_correct | Business Administration | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| e47becba:correct_paraphrase | I graduated with a degree in Business Administration. | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| e47becba:clearly_wrong | I graduated with a Computer Science degree. | no | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| 6a1eabeb:known_correct | 25 minutes and 50 seconds | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| 6a1eabeb:correct_paraphrase | My best was 25:50. | yes | NOT RUN | NOT RUN | not_run | No paid API call was made. |
| 6a1eabeb:clearly_wrong | My personal best was 31 minutes. | no | NOT RUN | NOT RUN | not_run | No paid API call was made. |

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': 'e47becba', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '118b2229', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '51a45a95', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '58bf7951', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '1e043500', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'c5e8278d', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6ade9755', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6f9b354f', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '7161e7e2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'c4f10528', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '89527b6b', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'e9327a54', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '4c36ccef', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6ae235be', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '7e00a6cb', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '1903aded', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '8a2466db', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '06878be2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '75832dbd', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '0edc2aef', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '35a27287', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '32260d93', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '195a1a1b', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'afdc33df', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'caf03d32', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '0a995998', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6d550036', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_59c863d7', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'b5ef892d', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'e831120c', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '3a704032', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_d84a3211', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'aae3761f', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_59149c77', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_f49edff3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '71017276', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'b46e15ed', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_fa19884c', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '0bc8ad92', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'af082822', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_4929293a', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6a1eabeb', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6aeb4375', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '830ce83f', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '852ce960', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '945e3d21', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'd7c942c3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '71315a70', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '89941a93', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'ce6d2d27', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `3.65515456`
- Reported system cost, excluding judge: `0.0`
- Internal judging cost: `0.0`
- Total API spend: `0.0`
