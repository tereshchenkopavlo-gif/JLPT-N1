# v186 — C10 source and author review

Base: published v185, HTML SHA-256 `0cc48969700d238c27e7c3d4f18773ab31508257b0b11a544e5b15f83a178042`.
Scope: IDs 565, 571, 572, 579, 586, 588, 590, 593, 595, 597, 599, 609.
The v153 pilot rows for these IDs were treated as hypotheses. Every current field, both Japanese examples, and both Ukrainian translations were reread from v185 before a decision.

## Decisions

| ID | Entry | Decision | Finding and action |
|---:|---|---|---|
| 565 | 順調 | fixed_rechecked | The first translation blurred 予定どおり and 見込みだ. It now preserves both the schedule and the forecast: “Роботи йдуть добре, і, як очікується, їх завершать наступного місяця за графіком.” The definition, gloss, second example and usage remain unchanged. |
| 571 | 盛大 | fixed_rechecked | The second translation narrowed 退職 to retirement. The neutral “відхід із роботи” does not assume age or retirement; 盛大な送別会 is rendered as a grand farewell event. |
| 572 | 積極的 | fixed_rechecked | The Japanese definition includes both taking initiative and a positive/supportive stance. The Ukrainian gloss now includes “прихильний до чогось, такий, що позитивно оцінює й підтримує”; examples remain unchanged. |
| 579 | 地味 | fixed_rechecked | The first translation incorrectly made “results” the object of accumulation. It now keeps 積み重ね as repeated, inconspicuous work: “Саме послідовна малопомітна праця й дає великі результати.” |
| 586 | 典型的 | fixed_rechecked | 典型的な英雄像 is a typical image/model of a hero. The second translation now preserves “типовий образ героя” rather than recasting it as “a typical hero.” |
| 588 | 独特 | pending_C11 | The examples and translations are acceptable. The dictionary classifies 独特 as 名・形動, while the current app POS map is only ナ形. Do not silently change the label: a separate C11 decision must evaluate quiz-pool and cloze consequences. No card data changed. |
| 590 | 否定的 | fixed_rechecked | 真摯に受け止める means to take the criticism/evaluation seriously. “Сумлінно приймати” was an unnatural calque; it is now “серйозно ставитися до негативних оцінок”. |
| 593 | 平気 | fixed_rechecked | The first translation attached the lack of composure to the act of being late. It now makes the attitude explicit: repeated lateness after warnings “наче нічого не сталося.” The second example and usage remain unchanged. |
| 595 | 未熟 | fixed_rechecked | 取り返しのつかない describes irreparable consequences, not an “irreparable accident.” The first translation now says “аварії з непоправними наслідками.” |
| 597 | 無難 | fixed_rechecked | “Нікого не дратівливими думками” was ungrammatical and semantically imprecise. It is replaced with “нейтральними висловлюваннями, що нікого не зачіпали,” preserving the safe/inoffensive sense of 無難な意見. |
| 599 | 無礼 | pending_C11 | The examples and translations are acceptable. The usage includes nominal 無礼を詫びる and Daijisen labels 無礼 as 名・形動, while the app POS map is only ナ形. Keep pending for separate C11 quiz-impact review; no data changed. |
| 609 | わりに | fixed_rechecked | The connection formula was ambiguous (“いAの普通形”). It now distinguishes noun の, verb plain form, i-adjective plain form, and na-adjective な before わりに. Both examples are appropriate. |

## Source checks

- Shogakukan Digital Daijisen via Kotobank: [退職](https://kotobank.jp/word/退職-179273), [盛大](https://kotobank.jp/word/盛大-545775), [積極的](https://kotobank.jp/word/積極的-548001), [地味](https://kotobank.jp/word/地味-523805), [典型的](https://kotobank.jp/word/典型的-577864), [独特](https://kotobank.jp/word/独特-582817), [否定的](https://kotobank.jp/word/否定的-611073), [平気](https://kotobank.jp/word/平気-128825), [未熟](https://kotobank.jp/word/未熟-637676), [無難](https://kotobank.jp/word/無難-620015), [無礼](https://kotobank.jp/word/無礼-589872).
- [わりに connection reference](https://www.sigure.tw/learn-japanese/grammar/n3/130): noun + の, na-adjective + な, adjective/verb plain forms.
- The sources confirm the semantic distinctions used above. They do not settle the app's internal quiz eligibility for ID588/599; that remains C11 work.

## Scope boundary

- 10 cards fixed/rechecked; IDs 588 and 599 remain pending.
- 10 exact field updates across 10 cards; no Japanese example sentence was changed.
- No POS map, quiz target, comparison pair, learning algorithm, or progress-storage change.
- No card or ID was removed. Historical v153 evidence and earlier register decisions remain intact.
