# حالة وكيل التنفيذ (mahmoud-agent) — محدَّث 3 أغسطس 2026

## الوضع الحالي

| البند | القيمة |
|---|---|
| الإصدار | **0.7** — معروض صحيحاً على الرابط |
| الرابط | https://mahmoud-agent.onrender.com |
| المستودع | maxsusa2018-cpu/mahmoud-agent — ⚠️ **Public** |
| الاستضافة | Render — Starter · Oregon · قرص دائم على `/var/data` |
| Auto-Deploy | ✅ شغّال — يلتقط الرفع من `main` تلقائياً |
| وضع التشغيل | ورقي فقط — `PAPER_MODE = True` |
| التنفيذ | `PaperBroker` معزول — إضافة Pionex = استبدال كلاس واحد |
| الإشارات | تصل فعلياً · **1234 حدثاً** في الدفتر |
| دفتر الظل | ✅ يعمل — كل `queued` يقابله `shadow` |
| المفاتيح | Environment Variables في Render فقط — لا تُكتب في الكود ولا تُشارَك |

### البوابتان والمقاعد

| | |
|---|---|
| بوابة هيكن `🚦HA` | 2 مقعد |
| بوابة الخام `🚦RAW` | 2 مقعد |
| استكشاف | 1 مقعد |
| `MAX_OPEN` / `MAX_DAILY_TRADES` | 5 / 5 |

**حالة 3 أغسطس مساءً:** البوابتان متفقتان · `LONG BTC فقط` · تعارض `false`
· صفر مفتوح · صفر طابور.

---

## 🔴 عطب أُصلح في 0.7 — فقدان الحالة عند إعادة النشر

**العَرَض (2-3 أغسطس):** خمس صفقات مفتوحة اختفت بلا حدث `CLOSE`،
والرصيد رجع لقيمته الابتدائية، والطابور من 95 إلى صفر. الدفتر نجا (1234
حدثاً ثابتة) — فالمشكلة في `state.json` لا في التخزين.

**السبب:** `save()` تحوّل حقلَي وقت فقط، وحقلا بوابة هيكن الجديدان
(`gate_ha_since` · `pending_ha_since`) يكسران `json.dump`. و`open(...,"w")`
تفرّغ الملف قبل الفشل — فكل حفظ يمسح الحفظة السابقة.

**أُصلح:** الحقول الأربعة · نسخة مستقلة لـ`positions` · كتابة ذرّية
(`.tmp` + `os.replace`) · إرجاع `opened_at` إلى `datetime`.

⚠️ **الاختبار الحاسم لم يتم بعد** — مثبت في المحاكاة، غير مثبت على السيرفر.
الدليل النهائي: إعادة نشر تصادف صفقة مفتوحة وتصمد.

---

## العقبة الحاكمة — Pionex Futures API

مؤكَّد من التوثيق الرسمي: **Futures API (REST + WebSocket) ما زال "Invite only"**.
مفتاح API عادي بصلاحية Trading **لا يفتح** مسارات `/uapi/v1` الخاصة بالفيوتشرز.

### صلاحيات المفتاح — ما يُفعَّل وما يُمنع

| الصلاحية | القرار | السبب |
|---|---|---|
| Enable reading | ✅ | قراءة المراكز والأوامر والرافعة |
| Enable trading | ✅ | إرسال وإلغاء الأوامر |
| Enable transfer | ❌ **ممنوع** | تحويل أموال بين الحسابات — أخطر بند متاح فعلياً |
| Bot reading / Bot trading | ❌ | الوكيل لا يستخدم بوتات Pionex |
| Earn (Beta) | ❌ | لا علاقة |
| Institutional deposit & withdrawal | ❌ | Invite only أصلاً |

**نقطة مطمئنة:** السحب غير متاح عبر مفاتيح API العادية إطلاقاً. أي مفتاح
عادي مسروق **لا يستطيع السحب**، لكنه يستطيع التحويل إن فُعِّلت
Enable transfer — لذلك تعطيلها إلزامي.

### تقييد IP

لم يُذكر خيار IP whitelist في التوثيق. إن ظهر، فالعناوين التي تُدرَج هي
**عناوين Render الصادرة** (Render Dashboard → الخدمة → Connect → Outbound
IP addresses)، لا عنوان الجوال أو المنزل.

---

## القاعدة المتفق عليها

⛔ لا ربط للتنفيذ الحقيقي قبل **أسبوع كامل** من المراقبة الورقية، والوكيل
يُثبت أنه يستقبل الإشارات ويعالجها صحيحاً.

⚠️ **بند إضافي (3 أغسطس):** ولا قبل إثبات صمود الحالة عبر إعادة نشر
فعلية بصفقة مفتوحة. صفقة مفتوحة على Pionex ينساها الوكيل = خطر حقيقي.

---

## رسالة طلب الصلاحية من دعم Pionex — نسخة إنجليزية

> **Subject:** Request for Perpetual Futures API access (invite-only)

> Hello Pionex Support,
>
> I am a Pionex user trading perpetual futures manually, and I have built a private tool for my own account only — no third-party users, no resale, no signal service.
>
> Your documentation marks the Futures API (REST and WebSocket) as invite only. Could you please advise on the following:
>
> 1. What is the process and what are the requirements to be granted **Perpetual Futures API** access on my account?
> 2. Can this be issued on a **sub-account with its own independent API key**, so my main account stays untouched?
> 3. Beyond the standard permission list, does the key for futures support **granular permissions** — trade-only, with transfer disabled?
> 4. Can the key be **restricted to a specific IP address** (whitelist)? My application runs from fixed outbound IPs.
>
> Intended use: automated order placement and position management for my own account, driven by my own TradingView-based analysis. Current stage is paper trading only; I will not connect live execution before the permissions above are confirmed.
>
> Thank you,
> Mahmoud

## نسخة عربية

> مرحباً فريق دعم Pionex،
>
> أنا مستخدم لدى Pionex وأتداول العقود الدائمة (Perpetual Futures) يدوياً، وقد بنيت أداة خاصة لحسابي وحدي — لا مستخدمين آخرين، لا إعادة بيع، ولا خدمة إشارات.
>
> توثيقكم يذكر أن Futures API (REST و WebSocket) بدعوة فقط، وأرجو إفادتي بالتالي:
>
> 1. ما إجراءات ومتطلبات منح صلاحية **Perpetual Futures API** على حسابي؟
> 2. هل يمكن إصدارها على **حساب فرعي بمفتاح API مستقل** حتى يبقى الحساب الرئيسي بعيداً؟
> 3. هل يدعم مفتاح الفيوتشرز **تحديد صلاحيات دقيقة** — تداول فقط مع تعطيل التحويل؟
> 4. هل يمكن **تقييد المفتاح بعنوان IP محدد** (قائمة بيضاء)؟ التطبيق يعمل من عناوين صادرة ثابتة.
>
> الاستخدام المقصود: إرسال الأوامر وإدارة المراكز آلياً لحسابي الشخصي فقط، بناءً على تحليلي عبر TradingView. المرحلة الحالية تداول ورقي فقط، ولن أربط التنفيذ الحقيقي قبل تأكيد الصلاحيات أعلاه.
>
> شكراً لكم،
> محمود

---

## الخطوات التالية بالترتيب

1. طلب الدعوة من الدعم (النص أعلاه) — **قبل أي كود تنفيذ**
2. ربط تنبيهات «القاع الخام» و«القمة الخام» بالويبهوك (البند 1 في الخارطة)
3. جمع 40 قيد ظل لكل بوابة لحسم هيكن مقابل الخام
4. إثبات صمود الحالة عبر إعادة نشر بصفقة مفتوحة
5. عند وصول الدعوة: كتابة `PionexBroker` بنفس واجهة `PaperBroker`،
   واختبارها على حساب فرعي بمفتاح reading+trading فقط
6. تشغيل حقيقي بحجم صغير جداً أولاً

---

## بنود صيانة مفتوحة

| # | البند | الأولوية |
|---|---|---|
| 1 | تحويل المستودع من Public إلى Private | متوسطة — المفاتيح في Render لا في الكود |
| 2 | تحويل الدفتر من JSONL إلى SQLite | تظهر عند تحليل 40+ قيداً لكل بوابة |
| 3 | توثيق وقت كل إعادة نشر | ⭐ يبدأ فوراً — لفصل العيّنات |

---

## مراجع رسمية

- [Pionex API Overview](https://www.pionex.com/docs/api-docs) — يوضح أن Futures API بدعوة فقط
- [API Key Permissions](https://www.pionex.com/docs/api-docs/references/api-key-permissions)
- [API Key Guide](https://www.pionex.com/docs/api-docs/references/api-key-guide)
- [Futures API — Common](https://www.pionex.com/docs/api-docs/futures-api/common) — Base URL: `https://api.pionex.com`
