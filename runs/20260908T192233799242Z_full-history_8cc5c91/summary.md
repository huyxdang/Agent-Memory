# LongMemEval five-question results

- Run ID: `20260908T192233799242Z_full-history_8cc5c91`
- System: `full-history`
- Run status: `running`
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
| e47becba | 110325 | 110531 | 1024 | 256 | 1050000 | 938189 | True |
| 118b2229 | 108598 | 108806 | 1024 | 256 | 1050000 | 939914 | True |
| 51a45a95 | 111144 | 111356 | 1024 | 256 | 1050000 | 937364 | True |
| 58bf7951 | 111305 | 111515 | 1024 | 256 | 1050000 | 937205 | True |
| 1e043500 | 110878 | 111089 | 1024 | 256 | 1050000 | 937631 | True |
| c5e8278d | 111322 | 111531 | 1024 | 256 | 1050000 | 937189 | True |
| 6ade9755 | 109589 | 109795 | 1024 | 256 | 1050000 | 938925 | True |
| 6f9b354f | 112015 | 112223 | 1024 | 256 | 1050000 | 936497 | True |
| 7161e7e2 | 109655 | 109885 | 1024 | 256 | 1050000 | 938835 | True |
| c4f10528 | 111105 | 111340 | 1024 | 256 | 1050000 | 937380 | True |
| 89527b6b | 111532 | 111766 | 1024 | 256 | 1050000 | 936954 | True |
| e9327a54 | 109775 | 110005 | 1024 | 256 | 1050000 | 938715 | True |
| 4c36ccef | 111327 | 111545 | 1024 | 256 | 1050000 | 937175 | True |
| 6ae235be | 109879 | 110113 | 1024 | 256 | 1050000 | 938607 | True |
| 7e00a6cb | 109851 | 110080 | 1024 | 256 | 1050000 | 938640 | True |
| 1903aded | 109410 | 109638 | 1024 | 256 | 1050000 | 939082 | True |
| 8a2466db | 111417 | 111630 | 1024 | 256 | 1050000 | 937090 | True |
| 06878be2 | 110896 | 111108 | 1024 | 256 | 1050000 | 937612 | True |
| 75832dbd | 108500 | 108713 | 1024 | 256 | 1050000 | 940007 | True |
| 0edc2aef | 111842 | 112053 | 1024 | 256 | 1050000 | 936667 | True |
| 35a27287 | 107642 | 107854 | 1024 | 256 | 1050000 | 940866 | True |
| 32260d93 | 109505 | 109717 | 1024 | 256 | 1050000 | 939003 | True |
| 195a1a1b | 110089 | 110301 | 1024 | 256 | 1050000 | 938419 | True |
| afdc33df | 112225 | 112442 | 1024 | 256 | 1050000 | 936278 | True |
| caf03d32 | 111023 | 111238 | 1024 | 256 | 1050000 | 937482 | True |
| 0a995998 | 111429 | 111645 | 1024 | 256 | 1050000 | 937075 | True |
| 6d550036 | 104748 | 104958 | 1024 | 256 | 1050000 | 943762 | True |
| gpt4_59c863d7 | 110665 | 110875 | 1024 | 256 | 1050000 | 937845 | True |
| b5ef892d | 110408 | 110623 | 1024 | 256 | 1050000 | 938097 | True |
| e831120c | 110016 | 110238 | 1024 | 256 | 1050000 | 938482 | True |
| 3a704032 | 111548 | 111758 | 1024 | 256 | 1050000 | 936962 | True |
| gpt4_d84a3211 | 109901 | 110118 | 1024 | 256 | 1050000 | 938602 | True |
| aae3761f | 109097 | 109313 | 1024 | 256 | 1050000 | 939407 | True |
| gpt4_59149c77 | 108763 | 108995 | 1024 | 256 | 1050000 | 939725 | True |
| gpt4_f49edff3 | 109737 | 109986 | 1024 | 256 | 1050000 | 938734 | True |
| 71017276 | 109705 | 109921 | 1024 | 256 | 1050000 | 938799 | True |
| b46e15ed | 111723 | 111942 | 1024 | 256 | 1050000 | 936778 | True |
| gpt4_fa19884c | 107909 | 108137 | 1024 | 256 | 1050000 | 940583 | True |
| 0bc8ad92 | 108916 | 109130 | 1024 | 256 | 1050000 | 939590 | True |
| af082822 | 111283 | 111498 | 1024 | 256 | 1050000 | 937222 | True |
| gpt4_4929293a | 111200 | 111414 | 1024 | 256 | 1050000 | 937306 | True |
| 6a1eabeb | 109643 | 109856 | 1024 | 256 | 1050000 | 938864 | True |
| 6aeb4375 | 108013 | 108223 | 1024 | 256 | 1050000 | 940497 | True |
| 830ce83f | 109372 | 109581 | 1024 | 256 | 1050000 | 939139 | True |
| 852ce960 | 109372 | 109589 | 1024 | 256 | 1050000 | 939131 | True |
| 945e3d21 | 111714 | 111926 | 1024 | 256 | 1050000 | 936794 | True |
| d7c942c3 | 111303 | 111514 | 1024 | 256 | 1050000 | 937206 | True |
| 71315a70 | 111108 | 111319 | 1024 | 256 | 1050000 | 937401 | True |
| 89941a93 | 111209 | 111416 | 1024 | 256 | 1050000 | 937304 | True |
| ce6d2d27 | 110484 | 110696 | 1024 | 256 | 1050000 | 938024 | True |

## Tracking summary

Fixed tokenizer: `o200k_base`. Output tokens include reasoning tokens; non-reasoning output is output minus reasoning.

| Stage | Input tokens | Output tokens (inclusive) | Reasoning subset | Non-reasoning output | Cost USD | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Memory writing (not applicable) | 0 | 0 | 0 | 0 | 0.0 | 0.0 |
| Answering | 1771186 | 434 | 0 | 434 | 0.354758 | 31.5018 |
| Judge (internal only) | 32366 | 8022 | 7360 | 662 | 0.0913015 | 209.6979 |

- Reported system cost (judge excluded): `0.354758`
- Total API spend (judge included): `0.4460595`

## Answers and grades

| ID | Type | Question | Reference answer | Generated answer | Verdict | Judge explanation | Status |
|---|---|---|---|---|---|---|---|
| e47becba | single-session-user | What degree did I graduate with? | Business Administration | You graduated with a degree in **Business Administration** (conversation dated **May 30, 2023, 17:27**). | yes | Core claim: Identify the degree the user graduated with. Correct answer: Business Administration. <br>Model response states explicitly: "You graduated with a degree in Business Administration." This matches exactly. The added conversation date is extraneous but does not contradict or alter the core answer. Therefore, it's equivalent and acceptable. | success |
| 118b2229 | single-session-user | How long is my daily commute to work? | 45 minutes each way | Your daily commute is **45 minutes each way**, or **90 minutes total per day**. | yes | Reasoning steps omitted. | success |
| 51a45a95 | single-session-user | Where did I redeem a $5 coupon on coffee creamer? | Target | You redeemed the $5 coupon at **Target**. | yes | NOT RUN | success |
| 58bf7951 | single-session-user | What play did I attend at the local community theater? | The Glass Menagerie | You attended a production of **_The Glass Menagerie_** at the local community theater. | yes | NOT RUN | success |
| 1e043500 | single-session-user | What is the name of the playlist I created on Spotify? | Summer Vibes | The playlist you created on Spotify is called **“Summer Vibes.”** | yes | The model response exactly matches the correct answer “Summer Vibes.” | success |
| c5e8278d | single-session-user | What was my last name before I changed it? | Johnson | Your last name before you changed it was **Johnson**. | yes | The correct answer is "Johnson." The model response states the last name before the change was "Johnson," which matches exactly. No contradictions or omissions. | success |
| 6ade9755 | single-session-user | Where do I take yoga classes? | Serenity Yoga | You take yoga classes at **Serenity Yoga**. You also practice at home using the **Down Dog** app. | yes | NOT RUN | success |
| 6f9b354f | single-session-user | What color did I repaint my bedroom walls? | a lighter shade of gray | You repainted your bedroom walls a lighter shade of gray. | yes | I can’t share detailed reasoning, but the model’s answer matches the specified color exactly. | success |
| 7161e7e2 | single-session-assistant | I'm checking our previous chat about the shift rotation sheet for GM social media agents. Can you remind me what was the rotation for Admon on a Sunday? | Admon was assigned to the 8 am - 4 pm (Day Shift) on Sundays. | For **Admon**, the Sunday shift was **8:00 am–4:00 pm**. | yes | The model exactly matches the Sunday 8:00 am–4:00 pm assignment; naming "Day Shift" is not required. | success |
| c4f10528 | single-session-assistant | I'm planning to visit Bandung again and I was wondering if you could remind me of the name of that restaurant in Cihampelas Walk that serves a great Nasi Goreng? | Miss Bee Providore | The restaurant was **Miss Bee Providore**. It was recommended for its signature **Miss Bee’s Nasi Goreng**. | yes | NOT RUN | success |
| 89527b6b | single-session-assistant | I'm going back to our previous conversation about the children's book on dinosaurs. Can you remind me what color was the scaly body of the Plesiosaur in the image? | The Plesiosaur had a blue scaly body. | The Plesiosaur’s scaly body was described as **blue**. | yes | Cannot provide detailed reasoning, but the response matches the correct answer. | success |
| e9327a54 | single-session-assistant | I'm planning to revisit Orlando. I was wondering if you could remind me of that unique dessert shop with the giant milkshakes we talked about last time? | The Sugar Factory at Icon Park. | The dessert shop was **The Sugar Factory**, located at **ICON Park** in Orlando. It’s known for enormous specialty drinks and giant milkshakes. | yes | Core claim: Identify the unique dessert shop with giant milkshakes previously discussed—correct answer is "The Sugar Factory at Icon Park."<br>Model response: Names "The Sugar Factory," specifies location at ICON Park in Orlando, and mentions giant milkshakes.<br>This directly matches the correct answer with accurate added context. No contradictions or omissions. | success |
| 4c36ccef | single-session-assistant | Can you remind me of the name of the romantic Italian restaurant in Rome you recommended for dinner? | Roscioli | The romantic Italian restaurant I recommended was **Roscioli**. | yes | NOT RUN | success |
| 6ae235be | single-session-assistant | I remember you told me about the refining processes at CITGO's three refineries earlier. Can you remind me what kind of processes are used at the Lake Charles Refinery? | Atmospheric distillation, fluid catalytic cracking (FCC), alkylation, and hydrotreating. | At CITGO’s **Lake Charles Refinery**, the earlier response listed these main processes:<br><br>- **Atmospheric distillation:** Heats crude oil and separates it into fractions according to boiling points.<br>- **Fluid catalytic cracking (FCC):** Converts heavier crude-oil fractions into lighter, higher-value products such as gasoline and diesel.<br>- **Alkylation:** Combines smaller hydrocarbon molecules to produce high-octane gasoline components.<br>- **Hydrotreating:** Removes sulfur and other impurities from gasoline and diesel streams to improve product quality. | yes | NOT RUN | success |
| 7e00a6cb | single-session-assistant | I'm planning my trip to Amsterdam again and I was wondering, what was the name of that hostel near the Red Light District that you recommended last time? | International Budget Hostel | The hostel was **International Budget Hostel**, located near Amsterdam’s Red Light District. | yes | NOT RUN | success |
| 1903aded | single-session-assistant | I think we discussed work from home jobs for seniors earlier. Can you remind me what was the 7th job in the list you provided? | Transcriptionist. | The 7th job listed was **Transcriptionist**. | NOT RUN | NOT RUN | answer_complete |
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
| e47becba | 110529 | 31 | 0 | 31 | 0.022143 | 2.6513 | gpt-5.6-luna |
| 118b2229 | 108804 | 22 | 0 | 22 | 0.0217872 | 2.1421 | gpt-5.6-luna |
| 51a45a95 | 111354 | 14 | 0 | 14 | 0.0222876 | 1.907 | gpt-5.6-luna |
| 58bf7951 | 111513 | 22 | 0 | 22 | 0.022329 | 1.656 | gpt-5.6-luna |
| 1e043500 | 111087 | 18 | 0 | 18 | 0.022239 | 1.9698 | gpt-5.6-luna |
| c5e8278d | 111529 | 15 | 0 | 15 | 0.0223238 | 1.7898 | gpt-5.6-luna |
| 6ade9755 | 109793 | 27 | 0 | 27 | 0.021991 | 2.8549 | gpt-5.6-luna |
| 6f9b354f | 112221 | 15 | 0 | 15 | 0.0224622 | 1.5794 | gpt-5.6-luna |
| 7161e7e2 | 109883 | 24 | 0 | 24 | 0.0220054 | 1.5631 | gpt-5.6-luna |
| c4f10528 | 111338 | 29 | 0 | 29 | 0.0223024 | 1.9003 | gpt-5.6-luna |
| 89527b6b | 111764 | 19 | 0 | 19 | 0.0223756 | 1.5914 | gpt-5.6-luna |
| e9327a54 | 110003 | 34 | 0 | 34 | 0.0220414 | 1.613 | gpt-5.6-luna |
| 4c36ccef | 111543 | 16 | 0 | 16 | 0.0223278 | 2.0943 | gpt-5.6-luna |
| 6ae235be | 110111 | 113 | 0 | 113 | 0.0221578 | 2.5363 | gpt-5.6-luna |
| 7e00a6cb | 110078 | 19 | 0 | 19 | 0.0220384 | 1.869 | gpt-5.6-luna |
| 1903aded | 109636 | 16 | 0 | 16 | 0.0219464 | 1.7841 | gpt-5.6-luna |
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
| e47becba | 1535 | 273 | 192 | 81 | 0.00306475 | 6.8172 | gpt-5-2025-08-07 |
| 118b2229 | 1531 | 344 | 320 | 24 | 0.00391375 | 7.3241 | gpt-5-2025-08-07 |
| 51a45a95 | 1523 | 394 | 384 | 10 | 0.00440375 | 9.0473 | gpt-5-2025-08-07 |
| 58bf7951 | 1532 | 266 | 256 | 10 | 0.002991 | 5.9142 | gpt-5-2025-08-07 |
| 1e043500 | 1528 | 480 | 448 | 32 | 0.005126 | 9.3044 | gpt-5-2025-08-07 |
| c5e8278d | 1521 | 434 | 384 | 50 | 0.00465725 | 10.5515 | gpt-5-2025-08-07 |
| 6ade9755 | 1531 | 586 | 576 | 10 | 0.00618975 | 11.5282 | gpt-5-2025-08-07 |
| 6f9b354f | 1524 | 486 | 448 | 38 | 0.005181 | 10.7965 | gpt-5-2025-08-07 |
| 7161e7e2 | 1569 | 557 | 512 | 45 | 0.00609125 | 12.8928 | gpt-5-2025-08-07 |
| c4f10528 | 1564 | 330 | 320 | 10 | 0.003671 | 7.1548 | gpt-5-2025-08-07 |
| 89527b6b | 1560 | 608 | 576 | 32 | 0.006446 | 12.5516 | gpt-5-2025-08-07 |
| e9327a54 | 1566 | 215 | 128 | 87 | 0.0025235 | 4.0176 | gpt-5-2025-08-07 |
| 4c36ccef | 1533 | 202 | 192 | 10 | 0.00249625 | 4.7778 | gpt-5-2025-08-07 |
| 6ae235be | 1662 | 266 | 256 | 10 | 0.0032975 | 5.8105 | gpt-5-2025-08-07 |
| 7e00a6cb | 1547 | 202 | 192 | 10 | 0.00236975 | 5.0719 | gpt-5-2025-08-07 |
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
| validation:e47becba:known_correct | 1510 | 603 | 576 | 27 | 0.0063335 | 22.4461 | gpt-5-2025-08-07 |
| validation:e47becba:correct_paraphrase | 1516 | 287 | 256 | 31 | 0.004765 | 6.7528 | gpt-5-2025-08-07 |
| validation:e47becba:clearly_wrong | 1515 | 330 | 320 | 10 | 0.00360975 | 9.4125 | gpt-5-2025-08-07 |
| validation:6a1eabeb:known_correct | 1533 | 357 | 320 | 37 | 0.00548625 | 16.7448 | gpt-5-2025-08-07 |
| validation:6a1eabeb:correct_paraphrase | 1533 | 479 | 448 | 31 | 0.00512225 | 23.2196 | gpt-5-2025-08-07 |
| validation:6a1eabeb:clearly_wrong | 1533 | 323 | 256 | 67 | 0.00356225 | 7.5617 | gpt-5-2025-08-07 |

## Judge validation

| Case | Supplied answer | Expected | Actual | Agreement | Status | Detail |
|---|---|---|---|---|---|---|
| e47becba:known_correct | Business Administration | yes | yes | True | success |  |
| e47becba:correct_paraphrase | I graduated with a degree in Business Administration. | yes | yes | True | success |  |
| e47becba:clearly_wrong | I graduated with a Computer Science degree. | no | no | True | success |  |
| 6a1eabeb:known_correct | 25 minutes and 50 seconds | yes | yes | True | success |  |
| 6a1eabeb:correct_paraphrase | My best was 25:50. | yes | yes | True | success |  |
| 6a1eabeb:clearly_wrong | My personal best was 31 minutes. | no | no | True | success |  |

## Accounting and failures

- All selected questions exactly once: `True`
- Missing IDs: `[]`
- Duplicate or wrong-count IDs: `[]`
- Unexpected IDs: `[]`
- Failures: `[{'question_id': '1903aded', 'status': 'answer_complete', 'detail': ''}, {'question_id': '8a2466db', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '06878be2', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '75832dbd', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '0edc2aef', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '35a27287', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '32260d93', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '195a1a1b', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'afdc33df', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'caf03d32', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '0a995998', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6d550036', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_59c863d7', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'b5ef892d', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'e831120c', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '3a704032', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_d84a3211', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'aae3761f', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_59149c77', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_f49edff3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '71017276', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'b46e15ed', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_fa19884c', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '0bc8ad92', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'af082822', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'gpt4_4929293a', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6a1eabeb', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '6aeb4375', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '830ce83f', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '852ce960', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '945e3d21', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'd7c942c3', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '71315a70', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': '89941a93', 'status': 'not_run', 'detail': 'No paid API call was made.'}, {'question_id': 'ce6d2d27', 'status': 'not_run', 'detail': 'No paid API call was made.'}]`
- Projected maximum cost: `3.65649076`
- Reported system cost, excluding judge: `0.354758`
- Internal judging cost: `0.0913015`
- Total API spend: `0.4460595`
