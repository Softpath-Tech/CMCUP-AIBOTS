# Multilingual System Stress Test Report

**Date:** 2025-12-28 14:49:43
**Total Questions:** 60

## 1. Executive Summary
- **Success Rate:** 38/60 (63.3%)
- **Data Gaps (Fallback):** 22/60 (36.7%)
- **System Stability:** 100.0% Error Free
- **Avg Latency:** `2.24s`

## 2. Language Performance
| Language | Total | Success | Fallback | Success % | Avg Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| English | 20 | 15 | 5 | 75.0% | 2.58s |
| Hindi | 20 | 12 | 8 | 60.0% | 2.31s |
| Telugu | 20 | 11 | 9 | 55.0% | 1.84s |

## 3. Topic Performance
| Topic | Total | Success | Fallback | Success % |
| :--- | :--- | :--- | :--- | :--- |
| Events | 9 | 3 | 6 | 33.3% |
| Fixtures | 9 | 9 | 0 | 100.0% |
| General | 15 | 11 | 4 | 73.3% |
| Locations | 12 | 9 | 3 | 75.0% |
| Policy | 15 | 6 | 9 | 40.0% |

## 4. Full Results Log
| ID | Lang | Topic | STS | Latency | Model | Question | Answer |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | English | General | SUCCESS | 2.02s | gpt-4o-mini-2024-07-18 | Who is the CM of Telangana? | The Chief Minister of Telangana is Sri A. Revanth Reddy. |
| 2 | Hindi | General | SUCCESS | 1.93s | gpt-4o-mini-2024-07-18 | Telangana ka CM kaun hai? | The Chief Minister of Telangana is Sri A. Revanth Reddy. |
| 3 | Telugu | General | SUCCESS | 1.95s | gpt-4o-mini-2024-07-18 | Telangana CM evaru? | The Chief Minister of Telangana is Sri A. Revanth Reddy. |
| 4 | English | Policy | SUCCESS | 2.69s | gpt-4o-mini-2024-07-18 | What is the sports policy of Telangana? | The Telangana Sports Policy (TSP) aims to establish Telangana as a global sports leader by fostering sustainable all-round development across various  |
| 5 | Hindi | Policy | FALLBACK | 1.76s | gpt-4o-mini-2024-07-18 | Telangana ki sports policy kya hai? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 6 | Telugu | Policy | FALLBACK | 1.85s | gpt-4o-mini-2024-07-18 | Telangana kreeda vidhanam emiti? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 7 | English | Locations | SUCCESS | 1.6s | gpt-4o-mini-2024-07-18 | Which district does Charminar belong to? | Charminar belongs to the District of Hyderabad. |
| 8 | Hindi | Locations | SUCCESS | 1.25s | gpt-4o-mini-2024-07-18 | Charminar kis zile mein hai? | Charminar is located in the District of Hyderabad. |
| 9 | Telugu | Locations | FALLBACK | 1.35s | gpt-4o-mini-2024-07-18 | Charminar ee jilla lo undi? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 10 | English | Fixtures | SUCCESS | 1.34s | gpt-4o-mini-2024-07-18 | When is Match ID 24 scheduled? | Match ID 24 is scheduled for Day-1 at 17:10. It is between Ranga Reddy and Mancherial. |
| 11 | Hindi | Fixtures | SUCCESS | 3.44s | gpt-4o-mini-2024-07-18 | Match ID 24 kab hai? | Match ID 24 is scheduled for **Day-1** at **01:00 PM**. The match is between **Adilabad** and **Kumuram bheem (asifabad)**. |
| 12 | Telugu | Fixtures | SUCCESS | 3.26s | gpt-4o-mini-2024-07-18 | Match ID 24 eppudu jaruguthundi? | Match ID 24 has multiple matches scheduled. Here are the details:  1. Match **M-24** (Fixture ID: 461) is scheduled for **Day-1** at **17:10**. 2. Mat |
| 13 | English | General | SUCCESS | 1.27s | gpt-4o-mini-2024-07-18 | Contact number for helpdesk | The official contact number for the Sports Authority of Telangana is **040-23240247**. |
| 14 | Hindi | General | SUCCESS | 1.76s | gpt-4o-mini-2024-07-18 | Helpdesk ka number kya hai? | The official landline contact number for the Sports Authority of Telangana is **040-23240247**. |
| 15 | Telugu | General | FALLBACK | 1.86s | gpt-4o-mini-2024-07-18 | Helpdesk number emiti? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 16 | English | Events | FALLBACK | 2.17s | gpt-4o-mini-2024-07-18 | What is the schedule for Kabaddi? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 17 | Hindi | Events | FALLBACK | 2.16s | gpt-4o-mini-2024-07-18 | Kabaddi ka schedule kya hai? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 18 | Telugu | Events | FALLBACK | 1.98s | gpt-4o-mini-2024-07-18 | Kabaddi schedule emiti? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 19 | English | Policy | SUCCESS | 2.44s | gpt-4o-mini-2024-07-18 | Incentives for coaches? | Coaches will be categorized into three tiers: Elite, Emerging, and Foundation Categories, based on their qualifications, experience, results delivered |
| 20 | Hindi | Policy | FALLBACK | 2.68s | gpt-4o-mini-2024-07-18 | Coaches ke liye kya incentives hain? | Coaches will receive incentives based on a three-tier structure categorized into Elite, Emerging, and Foundation Categories. These categories are dete |
| 21 | Telugu | Policy | SUCCESS | 1.94s | gpt-4o-mini-2024-07-18 | Coaches ki incentives emiti? | Coaches will be categorized into three tiers: Elite, Emerging, and Foundation Categories, based on their qualifications, experience, results delivered |
| 22 | English | Locations | SUCCESS | 1.14s | gpt-4o-mini-2024-07-18 | Is Warangal a registered district? | Yes, Warangal is a registered district in Telangana, with the ID 32. |
| 23 | Hindi | Locations | FALLBACK | 1.35s | gpt-4o-mini-2024-07-18 | Kya Warangal ek registered zila hai? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 24 | Telugu | Locations | SUCCESS | 1.54s | gpt-4o-mini-2024-07-18 | Warangal oka registered jilla na? | Yes, Warangal is a registered district in Telangana. |
| 25 | English | Events | SUCCESS | 3.76s | gpt-4o-mini-2024-07-18 | List all events for Wrestling. | Here are all the events for Wrestling:  1. 55kg 2. 60kgs 3. 50-57kgs 4. 61kg 5. 65kg 6. 70kg 7. 74kgs 8. 44-45kgs 9. 48kg 10. 51kg 11. 53 12. 55 13. 5 |
| 26 | Hindi | Events | SUCCESS | 5.66s | gpt-4o-mini-2024-07-18 | Wrestling ke saare events batao. | Here are all the events related to Wrestling:  1. Event **53** (ID: 34) 2. Event **55** (ID: 34) 3. Event **57** (ID: 34) 4. Event **59** (ID: 34) 5.  |
| 27 | Telugu | Events | SUCCESS | 3.56s | gpt-4o-mini-2024-07-18 | Wrestling ki sambandinchina anni events cheppandi. | Here are all the events related to Wrestling:  1. 55kg 2. 60kgs 3. 50-57kgs 4. 61kg 5. 65kg 6. 70kg 7. 74kgs 8. 53 9. 55 10. 57 11. 59 12. 44-45kgs 13 |
| 28 | English | General | SUCCESS | 1.5s | gpt-4o-mini-2024-07-18 | Address of the main stadium | The main stadium of the Sports Authority of Telangana is located at:  **L.B. Stadium, Basheerbagh, Hyderabad -- 500001, Telangana, India**. |
| 29 | Hindi | General | SUCCESS | 1.51s | gpt-4o-mini-2024-07-18 | Main stadium ka pata kya hai? | The main stadium of the Sports Authority of Telangana is located at:  **L.B. Stadium, Basheerbagh, Hyderabad -- 500001, Telangana, India**. |
| 30 | Telugu | General | SUCCESS | 1.48s | gpt-4o-mini-2024-07-18 | Main stadium address emiti? | The main stadium address is **L.B. Stadium, Basheerbagh, Hyderabad -- 500001, Telangana, India**. |
| 31 | English | Fixtures | SUCCESS | 2.21s | gpt-4o-mini-2024-07-18 | Who is playing in Match ID 55? | Match ID 55 is between **Nalgonda** and **Karimnagar**. |
| 32 | Hindi | Fixtures | SUCCESS | 2.64s | gpt-4o-mini-2024-07-18 | Match ID 55 mein kaun khel raha hai? | Match ID 55 is between **Nalgonda** and **Karimnagar**. |
| 33 | Telugu | Fixtures | SUCCESS | 2.16s | gpt-4o-mini-2024-07-18 | Match ID 55 lo evaru aduthunnaru? | Match ID 55 is scheduled for Day-2 at 12:00 PM, and it is between **Nalgonda** and **Karimnagar**. |
| 34 | English | Policy | FALLBACK | 2.03s | gpt-4o-mini-2024-07-18 | Reservation policy for athletes? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 35 | Hindi | Policy | FALLBACK | 1.72s | gpt-4o-mini-2024-07-18 | Athletes ke liye reservation policy kya hai? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 36 | Telugu | Policy | FALLBACK | 1.33s | gpt-4o-mini-2024-07-18 | Athletes kosam reservation policy emiti? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 37 | English | Locations | SUCCESS | 14.31s | gpt-4o-mini-2024-07-18 | Details for Karimnagar district. | Karimnagar district has several mandals and clusters. Here are the details:  **Mandal Information:** 1. **Ganneruvaram** - Assembly Constituency: MANA |
| 38 | Hindi | Locations | SUCCESS | 6.51s | gpt-4o-mini-2024-07-18 | Karimnagar zile ki details. | Karimnagar district (ID: 10) includes several mandals and clusters. Here are the details:  **Mandals in Karimnagar District:** 1. Nizamsagar (ID: 165) |
| 39 | Telugu | Locations | FALLBACK | 2.26s | gpt-4o-mini-2024-07-18 | Karimnagar jilla vivaralu. | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 40 | English | General | SUCCESS | 2.57s | gpt-4o-mini-2024-07-18 | What is the CM Cup? | The Chief Minister's Cup (CM Cup) is a structured sports competition organized by the Sports Authority of Telangana (SATG). It follows a five-tier com |
| 41 | Hindi | General | SUCCESS | 3.15s | gpt-4o-mini-2024-07-18 | CM Cup kya hai? | The Chief Minister's Cup (CM Cup) is a structured sports competition framework organized by the Sports Authority of Telangana (SATG). It consists of a |
| 42 | Telugu | General | SUCCESS | 2.22s | gpt-4o-mini-2024-07-18 | CM Cup ante emiti? | The CM Cup, or Chief Minister's Cup, is a structured competition framework organized by the Sports Authority of Telangana (SATG). It follows a five-ti |
| 43 | English | Events | FALLBACK | 1.54s | gpt-4o-mini-2024-07-18 | Venue for Athletics matches? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 44 | Hindi | Events | FALLBACK | 1.67s | gpt-4o-mini-2024-07-18 | Athletics matches ka venue kya hai? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 45 | Telugu | Events | FALLBACK | 1.2s | gpt-4o-mini-2024-07-18 | Athletics matches jarige pradesham edhi? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 46 | English | Policy | SUCCESS | 1.44s | gpt-4o-mini-2024-07-18 | What is the cash award for Olympic Gold? | The cash award for winning a Gold medal at the Olympics is ₹6 Crore. |
| 47 | Hindi | Policy | SUCCESS | 1.27s | gpt-4o-mini-2024-07-18 | Olympic Gold ke liye cash award kya hai? | For the Olympics, athletes will receive ₹6 Crore for winning a Gold medal. |
| 48 | Telugu | Policy | SUCCESS | 1.23s | gpt-4o-mini-2024-07-18 | Olympic Gold ki cash award entha? | For the Olympics, athletes will receive ₹6 Crores for a Gold medal. |
| 49 | English | General | FALLBACK | 2.2s | gpt-4o-mini-2024-07-18 | Registration process for CM Cup | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 50 | Hindi | General | FALLBACK | 1.23s | gpt-4o-mini-2024-07-18 | CM Cup ke liye registration process kya hai? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 51 | Telugu | General | FALLBACK | 1.22s | gpt-4o-mini-2024-07-18 | CM Cup registration elaa cheyyali? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 52 | English | Fixtures | SUCCESS | 1.64s | gpt-4o-mini-2024-07-18 | When is Match ID 78 scheduled? | Match ID 78 is scheduled for DAY-2 at 06:50. |
| 53 | Hindi | Fixtures | SUCCESS | 2.07s | gpt-4o-mini-2024-07-18 | Match ID 78 kab hai? | Match ID 78 (Fixture ID: 540) is scheduled for DAY-2 at 06:50. It is between Adilabad and Jagithyal. |
| 54 | Telugu | Fixtures | SUCCESS | 1.63s | gpt-4o-mini-2024-07-18 | Match ID 78 eppudu? | Match ID 78 is scheduled for **Day-3** at **09:00 AM**. It is between **Medchal-malkajgiri** and **Narayanpet**. |
| 55 | English | Locations | SUCCESS | 2.13s | gpt-4o-mini-2024-07-18 | Is Hyderabad a district? | Yes, Hyderabad is a district. It has the ID '4' and the Code '04'. |
| 56 | Hindi | Locations | SUCCESS | 1.17s | gpt-4o-mini-2024-07-18 | Kya Hyderabad ek zila hai? | Yes, Hyderabad is a district in the state of Telangana. |
| 57 | Telugu | Locations | SUCCESS | 1.45s | gpt-4o-mini-2024-07-18 | Hyderabad oka jilla na? | Yes, Hyderabad is a district in Telangana. |
| 58 | English | Policy | FALLBACK | 1.5s | gpt-4o-mini-2024-07-18 | What is the budget for infrastructure? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 59 | Hindi | Policy | FALLBACK | 1.24s | gpt-4o-mini-2024-07-18 | Infrastructure ka budget kya hai? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
| 60 | Telugu | Policy | FALLBACK | 1.3s | gpt-4o-mini-2024-07-18 | Infrastructure budget entha? | I don't have that information. Please go to this website https://satg.telangana.gov.in/cmcup/ |
