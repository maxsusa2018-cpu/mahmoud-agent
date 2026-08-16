#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
  وكيل محمود — Pionex Perpetual Futures
  الإصدار 0.8-g · 16 أغسطس 2026 · وضع ورقي (لا تنفيذ حقيقي)
═══════════════════════════════════════════════════════════════

  المبدأ: المؤشرات حسّاسات تبلّغ فقط. هذا الملف هو العقل الوحيد.
  أربعة منها عمياء عن السوق — فالفيتو هنا مركزياً لا داخل السكربتات.

  ─────────────────────────────────────────────────────────────
  تغيير 0.8-g (16 أغسطس) — وصل السلك المفقود في إشارة الخروج
  ─────────────────────────────────────────────────────────────
  🔴 on_exit_signal كان يرمي الإشارة كاملة إن لم تبلغ الصفقة
     هدفها (`if not pos["half"]: continue`). القياس من الدفتر:
       · exit_signal_ignored = 543   (exit_bot 494 · exit_top 49)
       · exit_signal منفَّذة  = 348   (exit_bot 207 · exit_top 141)
     أي أن 61% من إشارات الخروج رُميت — والصفقة التي لم تربح
     شيئاً كانت محرومة من كل حماية عدا الستوب الأصلي، وهي
     بالضبط الصفقة الأحوج للحماية.
     وهذا يخالف قاعدة 31 يوليو: المرحلة 3 لا تشترط المرحلة 1.
     الإصلاح: الحارس أُزيل — إشارة الانعكاس تغلق الصفقة كما هي.

  🔴 والنسبة صارت مشروطة: 1.0 إن كانت الصفقة كاملة، و0.5 إن
     كان نصفها مغلقاً عند TP. كانت 0.5 ثابتة — ومع إزالة
     الحارس تصير الصفقة الكاملة تُغلق نصفها فقط، ولا تُزال
     (شرط 0.8-c يتطلب portion≥1.0 أو half=True) = عودة
     الصفقة الشبح. نفس صيغة الستوب في on_price بالضبط.

  ⚠️ سلوك الخروج تغيّر جوهرياً ⇒ CONFIG_VERSION رُفع.
     عيّنة 0.8-f تُقرأ منفصلة عمّا بعدها.

  ─────────────────────────────────────────────────────────────
  تغيير 0.8-e (14 أغسطس) — إصلاح دفتر الظل · لا تعديل منطق قرار
  ─────────────────────────────────────────────────────────────
  🔴 (1) متابعة الظل كانت تموت مع كل إعادة نشر.
         threading.Timer بأربع ساعات يعيش في الذاكرة وحدها، وأي
         نشر جديد أو إعادة تشغيل من الاستضافة يمسح كل المؤقتات
         المعلّقة. الوكيل نُشر مرات عديدة خلال أسبوعين، فجزء
         كبير من دفتر الظل ضاع بلا أثر — ولهذا لم يُنتج حكماً
         رغم آلاف الأحداث.
         الإصلاح: طابور على القرص الدائم + عامل يفحصه كل دقيقة.

  🔴 (2) سعر المتابعة كان يُقرأ من ST.last_price — أي من آخر
         تنبيه وصل لتلك العملة. فإن لم يصل تنبيه خلال الأربع
         ساعات، price_4h = None والقيد بلا نتيجة.
         الإصلاح: يُجلب مستقلاً من بينانس، كما يفعل وكيل التسجيل.

  🟢 (3) كل قيد ظل صار يحمل executed و reason و حالتي البوابتين.
         بهذا يصير السؤال الذي لم يُطرح قط قابلاً للإجابة:
         «الإشارات التي منعتها البوابة — كم منها كان سيربح؟»

  🟢 (4) مساران جديدان:
         /blocked/SECRET  — ملخّص الممنوع مقابل المنفَّذ
         /ledger/SECRET   — تصدير الدفتر الخام (?kind=... للفلترة)

  ⚠️ القيود المسجّلة قبل هذا الإصدار بلا executed/reason فتظهر
     تحت "?" — العدّ الحقيقي يبدأ من الآن.

  ─────────────────────────────────────────────────────────────
  تغيير 0.8-d (13 أغسطس) — إصلاح محاسبي · لا تعديل منطق قرار
  ─────────────────────────────────────────────────────────────
  🔴 سعر التنفيذ كان يُؤخذ من السعر الواصل مع التنبيه، لا من
     سعر الستوب/الهدف. والوكيل لا يرى السعر إلا لحظة وصول
     تنبيه — فقد يصل سعرٌ أبعد بكثير من الستوب. النتيجة:
       · breakeven_stop: 90 خسارة من 90، متوسط −26.1%
         والستوب على نقطة الدخول بالضبط ⇒ الصحيح 0.0%
       · stop_loss: −68.8% والستوب مضبوط على −50%
       · TP_half:   +33.1% للنصف والصحيح +25%
     صافي التشويه ≈ −23.8$ — الرصيد الحقيقي ≈ 97$ لا 73$.
     الإصلاح: الستوب يُنفَّذ عند pos["sl"]، والهدف عند tp_price().
     السعر الواصل يُحفظ في feed_price + feed_gap_pct للشفافية.
  ⚠️ الإغلاقات السابقة تبقى كما سُجّلت — «حسب الإصدار» يفصلها.

  ─────────────────────────────────────────────────────────────
  تغيير 0.8-c (13 أغسطس) — إصلاح · لا تعديل منطق قرار
  ─────────────────────────────────────────────────────────────
  🔴 (1) الصفقة الشبح — العطل الأخطر منذ بدء الاختبار.
         close_position كان يشيل الصفقة عند portion >= 1.0 فقط.
         لكن كل إغلاق بعد المرحلة الأولى نصفٌ (0.5):
           · الستوب على breakeven → 0.5
           · exit_signal          → 0.5
         فالصفقة تُغلق محاسبياً وتبقى في القائمة للأبد.
         النتيجة: المقاعد تمتلئ بموتى، وكل إشارة جديدة تُرفض
         slots_full، و«صفقات اليوم» تبقى صفراً بلا سبب ظاهر.
         مثبت بالمحاكاة على نسخة حرفية من الدالة.
         الإصلاح: تُزال أيضاً متى أُغلق النصف الثاني (half=True).

  🟡 (2) الفاصلة العائمة تُسقط الهدف عند الحد بالضبط:
         حركة 2% × 25x تعطي 49.9999999999997 وهي < 50 فلا يُنفَّذ.
         الإصلاح: هامش 1e-9.

  🟢 (3) سجل CLOSE أُثري: entry · side · src · gate_source ·
         conflict · مدة الصفقة · half. بدون gate_source لا يمكن
         حسم قاعدة البوابتين المسبقة يوم 21 أغسطس.

  🟢 (4) مصالحة المراكز عند الإقلاع: يُقرأ الدفتر، وأي مركز
         تثبت أسطرُه أن مجموع إغلاقاته ≥ 1.0 يُزال. يعالج
         الأشباح المتراكمة قبل هذا الإصدار — من بيانات حقيقية
         لا من تخمين.

  ⚠️ CONFIG_VERSION رُفع إلى 0.8-c عمداً: سلوك المقاعد تغيّر
     جوهرياً، فخلط ما قبل بما بعد يفسد التحليل. عيّنة 0.8-b
     تُقرأ منفصلة.

  ─────────────────────────────────────────────────────────────
  ما قبل ذلك (سجل التغييرات الأصلي)
  ─────────────────────────────────────────────────────────────
  تغيير 0.2:  «إجمالي الأحداث» كان يعدّ أسطر العرض (25 كحد أقصى)
              لا الأحداث الفعلية — والآن يعدّ كل سطر في الدفتر.

  تغيير 0.6:  البوابة صار لها حالة ثالثة فعلية: محايدة. قبل اليوم كانت
              الصفر حالة ابتدائية فقط لا يعود إليها الكود أبداً. الآن
              «خروج سيولة» أو «راقب» أو «محايد» تُصفّرها وتُلغي المعلّق —
              بشرط وجود «القرار:» في الرسالة، كي لا تبتلع كلمةٌ شائعة
              داخل تنبيه مؤشر بوابتَك خطأً.

  تغيير 0.5:  الإشارة المكررة على عملة مفتوحة تُوثَّق قبل رفضها:
              سعرها · سعر الدخول · الفارق % · الفارق بالدقائق · حكم
              مبدئي (تأكيد / سكين / غامض). السلوك لم يتغيّر — الرفض
              كما هو، لكن السجل صار قادراً على الفصل بعد أسبوع.

  تغيير 0.4:  الطابور — إشارة تُرفض بسبب البوابة تُحفظ SIGNAL_TTL_MIN
              دقيقة بدل أن تُنسى. لحظة فتح البوابة تُفحص وتُنفّذ إن
              وافقت اتجاهها. لا يتجاوز البوابة — ينتظرها.

  تغيير 0.3:  (1) الفتح الأول للبوابة من صفر صار فورياً. مهلة الأربع
                  ساعات تبقى على الانقلاب (LONG↔SHORT) وحده، حيث
                  توجد صفقات مفتوحة تستحق الحراسة.
              (2) انقلاب البوابة لم يعد يغلق الصفقات. يشدّ الستوب إلى
                  نقطة الدخول ويمنع الدخول الجديد فقط — الصفقة تُدار
                  بشروطها هي. السبب: تذبذب البوابة كان يذبح الصفقات.

  تغيير 0.7:  بوابتان متوازيتان — «هيكن» و«الخام» — كل منهما تصل عبر
              تنبيه ببادئته (🚦HA / 🚦RAW) ولها مقعداها المستقلان.
              لا مشاركة بين الميزانيتين: لو تقاسمتا مقعداً لفاز الأسرع
              دائماً، فيقيس الاختبار السرعة لا الجودة.
              + دفتر الظل: كل إشارة تُسجَّل ولو رُفضت، ومعها حالتا
                البوابتين وسعر ما بعد أربع ساعات. العيّنة ×5.
              + حقل gate_source على كل صفقة — هو الاختبار كله.

  قاعدة الحسم (مقفلة مسبقاً، لا تُعدَّل بعد رؤية النتائج):
              40 قيد ظل لكل بوابة أو 14 يوماً — أيهما أسبق.
              المقياس: نسبة الإشارات التي تحرّك السعر في الاتجاه
              المسموح بعد 4 ساعات.
              فارق ≥10 نقاط مئوية → الفائز يُعتمد والخاسر يُحذف.
              فارق <10 → يُعتمد هيكن (أبسط) ويُعاد القياس.

  التشغيل:   python3 agent.py
  الإيقاف الفوري:  أنشئ ملفاً اسمه KILL في نفس المجلد
  التقرير:   python3 agent.py --report

  بلا أي مكتبات خارجية — Python 3.8+ فقط.
"""

import json, os, re, sys, threading, time
import urllib.request
# طباعة فورية — بلا هذا لا تظهر السطور في سجل الاستضافة
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

# ═══════════════════════════════════════════════════════════════
#  الإعدادات — عدّل الأرقام هنا فقط، لا تلمس ما تحتها
# ═══════════════════════════════════════════════════════════════

PORT              = int(os.environ.get("PORT", 8080))  # السحابة تحدده تلقائياً
SECRET            = os.environ.get("SECRET", "mahmoud31")  # كلمة سر رابط الويبهوك
PAPER_MODE        = True        # True = يسجّل ولا ينفّذ. لا تغيّرها قبل أسبوعين.

MARGIN_USD        = 1.0         # هامش الصفقة الواحدة
LEVERAGE          = 25          # الرافعة
TP_PCT            = 50.0        # هدف المرحلة 1 (25x → 50% = حركة 2%)
SL_PCT            = 50.0        # الستوب الابتدائي (% من الهامش)
EPS               = 1e-9        # هامش الفاصلة العائمة عند مقارنة الهدف

CONFIG_VERSION    = "0.8-g"     # يُكتب مع كل حدث — سلوك الخروج تغيّر، فالعيّنة تُفصل

MAX_DAILY_TRADES  = 5           # حد الصفقات اليومي (كان 3 — رُفع ليكفي بوابتين)
MAX_OPEN          = 5           # 2 هيكن + 2 خام + 1 استكشاف
ONE_PER_TICKER    = True        # صفقة واحدة لكل عملة

# ── ميزانية المقاعد: ثابتة لكل بوابة، لا تُشارَك
#    مقعد شاغر في بوابة لا يُعطى للأخرى. يبقى شاغراً.
SLOT_HA           = 2
SLOT_RAW          = 2
SLOT_EXPLORE      = 1           # لنوع إشارة غير ممثَّل بين المفتوحات

SHADOW_FOLLOW_MIN = 240         # بعد كم دقيقة يُسجَّل سعر المتابعة للظل

EXEC_DELAY_SEC    = 150         # تأخير التنفيذ (فخ ما بعد الإغلاق — قاعدة 26 يونيو)
ADVERSE_CANCEL    = 0.4         # إن تحرّك السعر ضدك % خلال التأخير = ألغِ

GATE_FLIP_MIN     = 240         # انقلاب البوابة لا يُعتمد قبل 4 ساعات (درس 29 يوليو)
SIGNAL_TTL_MIN    = 45          # إشارة أقدم من هذا = منتهية الصلاحية

MAX_DRAWDOWN_PCT  = 30.0        # تراجع الرصيد = إيقاف تام
START_BALANCE     = 50.0

# نوافذ حظر الأخبار الحمراء — قاعدة Crypto Craft (فيتو 24 ساعة)
# الصيغة: ("2026-08-05 18:00", "اسم الخبر")  — بتوقيت UTC
RED_NEWS = [
    # ("2026-08-12 12:30", "CPI"),
    # ("2026-08-19 18:00", "FOMC"),
]

# مجلد البيانات — يوضع على القرص الدائم كي لا تُمسح عند إعادة النشر
BASE      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.environ.get("DATA_DIR", BASE)
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    _t = os.path.join(DATA_DIR, ".w"); open(_t, "w").close(); os.remove(_t)
except Exception as e:
    print(f"⚠️ تعذّر الكتابة في {DATA_DIR} ({e}) — الرجوع لمجلد السكربت", flush=True)
    DATA_DIR = BASE

KILL_FILE = os.path.join(DATA_DIR, "KILL")
LEDGER    = os.path.join(DATA_DIR, "ledger.jsonl")   # دفتر الظل — كل شيء
STATE_F   = os.path.join(DATA_DIR, "state.json")
SHADOW_F  = os.path.join(DATA_DIR, "shadow_pending.jsonl")  # 0.8-e — طابور المتابعة

# ═══════════════════════════════════════════════════════════════
#  قاموس الإشارات — يطابق نصوص تنبيهاتك الفعلية
# ═══════════════════════════════════════════════════════════════

# كلمات البوابة المحايدة — تُقرأ فقط مع «القرار:» (النسخة المشدَّدة)
NEUTRAL_KEYS = ("خروج سيولة", "راقب", "محايد")

# قرارات مقيّدة — تُقرأ محايدة (منع دخول جديد) لا لونج عام:
#   «LONG BTC فقط» = Alts ممنوعة | «تجنب Alts» | «Alts انتقائي» = بلا إذن عام
RESTRICTED_KEYS = ("BTC فقط", "تجنب", "انتقائي")

def classify(msg: str):
    """يحوّل نص التنبيه إلى (الدور، الاتجاه). الدور: gate/entry/exit_top/exit_bot/veto"""
    m = msg.replace("\u200f", "").strip()

    # ── البوابتان: تُميَّزان بالبادئة حصراً. رسالة بلا بادئة معروفة
    #    لا تُحدِّث أي بوابة — بدون هذا الحارس يفسد الاختبار من أول يوم.
    which = "ha" if m.startswith("🚦HA") else ("raw" if m.startswith("🚦RAW") else None)
    if which:
        role = "gate_" + which
        if "القرار:" in m and "Alts" in m:
            if "LONG" in m:  return (role, +1, "master_" + which)
            if "SHORT" in m: return (role, -1, "master_" + which)
        # المحايد يُفحص بعد LONG/SHORT عمداً كي لا يسبقهما
        if "القرار:" in m and any(k in m for k in NEUTRAL_KEYS):
            return (role, 0, "neutral_" + which)
        # قرارات لا تحمل «Alts» أو تحملها بلا LONG/SHORT — كانت تسقط
        # كـgate_bad_format فتبقى البوابة على قيمتها القديمة بصمت.
        # تُقرأ محايدة: «LONG BTC فقط» تمنع Alts، والوكيل بلا مفهوم
        # «بوابة مقيدة بعملة» — فالمنع أصدق من فتح لونج عام.
        if "القرار:" in m and any(k in m for k in RESTRICTED_KEYS):
            return (role, 0, "restricted_" + which)
        return (None, 0, "gate_bad_format")

    # ── بوابة قديمة بلا بادئة (نسخة Master ما قبل v15) — تُسجَّل ولا تُطبَّق
    if "القرار:" in m and ("Alts" in m or any(k in m for k in NEUTRAL_KEYS)):
        return (None, 0, "gate_unknown_prefix")

    # ── إشارات الخروج (ماستر)
    if "انعكاس قمة" in m and "مُنهَك" in m:      return ("exit_top", -1, "heikin_top")
    if "انعكاس قاع" in m and "مُنهَك" in m:      return ("exit_bot", +1, "heikin_bot")
    if "زناد قمة 3/3" in m:                      return ("exit_top", -1, "trigger_top")
    if "زناد قاع 3/3" in m:                      return ("exit_bot", +1, "trigger_bot")
    if "تصفية جارية" in m:                       return ("exit_bot", +1, "liquidation_harvest")

    # ── الفيتو
    if "BTC↓" in m and "BTC.D↓" in m:            return ("veto", 0, "liquidity_exit")

    # ── حالة السوق (Master) — تُفحص أولاً: رسالة سياق لا إشارة دخول
    if "MKT" in m and "BTC" in m:
        if "RANGE" in m: return ("mkt",  0, "market_state")
        if "DOWN"  in m: return ("mkt", -1, "market_state")
        if "UP"    in m: return ("mkt", +1, "market_state")

    # ── الزناد الخام (Master v15) — شرطان لحظيان بلا انتظار BTC 1h
    #    يُفحص قبل كتلة الدخول العامة: نصّه يحمل LONG/SHORT فيلتقطه
    #    الفحص العام كـ«unknown» لو تُرك بعده. مصدر منفصل عمداً
    #    كي يُقاس أداؤه ضد trigger_bot/trigger_top في الدفتر.
    if "قاع خام" in m:                           return ("entry", +1, "raw_bottom")
    if "قمة خام" in m:                           return ("entry", -1, "raw_top")

    # ── إشارات الدخول (المؤشرات الخمسة)
    up   = re.search(r"\b(LONG|BUY)\b", m, re.I) or "قاع جاهز" in m
    down = re.search(r"\b(SHORT|SELL)\b", m, re.I) or "قمة جاهزة" in m
    d = +1 if up and not down else (-1 if down and not up else 0)
    if d == 0:
        return (None, 0, "unknown")

    if "التقاء" in m:              return ("entry", d, "unified_confluence")  # 💎 الأقوى
    if "Unified" in m and "Early"   in m: return ("entry", d, "unified_early")
    if "Unified" in m and "Classic" in m: return ("entry", d, "unified_classic")
    if "Scanner B" in m:           return ("entry", d, "scanner_b")
    if "BB Rejection" in m:        return ("entry", d, "bb_rejection")
    if "Wolfe" in m:               return ("entry", d, "wolfe")
    if "Wyckoff" in m:             return ("entry", d, "wyckoff")
    return (None, d, "unknown")


# وزن كل مصدر — يُستخدم للترتيب عند تزاحم الإشارات، لا للقرار
WEIGHT = {"unified_confluence": 5, "unified_early": 4, "unified_classic": 4,
          "wyckoff": 3, "wolfe": 3, "raw_bottom": 3, "raw_top": 3,
          "scanner_b": 2, "bb_rejection": 2}

# الفريم المتوقع لكل دور — حماية من ربط الرابط بالنسخة الخطأ
EXPECTED_TF = {"master_raw": {"240", "4h"}, "master_ha": {"240", "4h"},
               "heikin_top": {"60", "1h"}, "heikin_bot": {"60", "1h"},
               "trigger_top": {"15"}, "trigger_bot": {"15"}}


# ═══════════════════════════════════════════════════════════════
#  الحالة
# ═══════════════════════════════════════════════════════════════

def now_utc(): return datetime.now(timezone.utc)
def today():   return now_utc().strftime("%Y-%m-%d")

def log(kind, data):
    """دفتر الظل — كل شيء يُسجّل: المقبول والمرفوض وسببه"""
    rec = {"ts": now_utc().isoformat(), "kind": kind, "cfg": CONFIG_VERSION, **data}
    try:
        with open(LEDGER, "a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        print("ledger error:", e)
    print(f"[{rec['ts'][11:19]}] {kind}: {json.dumps(data, ensure_ascii=False)[:160]}", flush=True)


class State:
    def __init__(self):
        # ── بوابتان مستقلتان تماماً. G["raw"] هي القديمة، G["ha"] الجديدة.
        self.gate_dir      = 0      # الخام — الاسم محفوظ للتوافق مع state.json القديم
        self.gate_since    = None
        self.pending_dir   = 0
        self.pending_since = None
        self.gate_ha       = 0      # هيكن
        self.gate_ha_since = None
        self.pending_ha    = 0
        self.pending_ha_since = None
        self.positions     = {}     # ticker -> dict
        self.day           = today()
        self.day_trades    = 0
        self.balance       = START_BALANCE
        self.peak          = START_BALANCE
        self.halted        = False
        self.last_price    = {}     # ticker -> (price, ts)
        # ── حالة سوق BTC وقت الإشارة (من تنبيه Master المستقل)
        #    تُختم على كل قيد ظل — بها نعرف: هل الأداة تعمل أم السوق يجاملها؟
        self.mkt           = "?"    # UP / DOWN / RANGE / ?
        self.mkt_adx       = None
        self.mkt_ts        = None
        self.load()

    # ── أسماء الحقول لكل بوابة (raw يحتفظ بالأسماء القديمة)
    F = {"raw": ("gate_dir", "gate_since", "pending_dir", "pending_since"),
         "ha":  ("gate_ha",  "gate_ha_since", "pending_ha", "pending_ha_since")}

    def gate(self, which):
        return getattr(self, self.F[which][0])

    # ── البوابة مع فلتر الانقلاب القصير — نفس المنطق، مطبَّق على أي بوابة
    def set_gate(self, d, ts, which="raw"):
        gd, gs, pd_, ps = self.F[which]
        if d == getattr(self, gd):
            setattr(self, pd_, 0)
            return "confirm"
        # ⭐ الفتح الأول من صفر = فوري. لا صفقات مفتوحة = لا شيء يُحرَس.
        if getattr(self, gd) == 0:
            setattr(self, gd, d); setattr(self, gs, ts); setattr(self, pd_, 0)
            return "open"
        # ── ما تحت هذا السطر انقلاب حقيقي (LONG↔SHORT) — الحراسة تبقى
        if getattr(self, pd_) != d:
            setattr(self, pd_, d); setattr(self, ps, ts)
            return "pending"
        # نفس الاتجاه المعلّق وصل مرة ثانية = تأكيد فوري
        setattr(self, gd, d); setattr(self, gs, ts); setattr(self, pd_, 0)
        return "flip"

    # ── البوابة المحايدة: لا اتجاه، ولا انتظار أربع ساعات
    def set_neutral(self, ts, which="raw"):
        """
        يُصفّر البوابة ويُلغي أي انقلاب معلّق. لا مهلة هنا:
        الحراسة الأربع-ساعات وُضعت لمنع دخول عكسي متسرّع، والمحايد
        لا يفتح شيئاً أصلاً — يمنع فقط. فتأخيره ضرر بلا مقابل.
        """
        gd, gs, pd_, ps = self.F[which]
        prev = getattr(self, gd)
        setattr(self, gd, 0); setattr(self, gs, ts)
        setattr(self, pd_, 0); setattr(self, ps, None)
        return prev

    def check_pending(self, now):
        """الانقلاب المعلّق يُعتمد إن نجا 4 ساعات بلا تناقض — للبوابتين"""
        for which in ("raw", "ha"):
            gd, gs, pd_, ps = self.F[which]
            pdir, psince = getattr(self, pd_), getattr(self, ps)
            if pdir and psince:
                if (now - psince).total_seconds() >= GATE_FLIP_MIN * 60:
                    setattr(self, gd, pdir); setattr(self, gs, now); setattr(self, pd_, 0)
                    log("gate", {"event": "flip_by_timeout", "gate": which, "dir": pdir})
                    on_gate_flip(pdir)   # نفس المعالجة: شدّ الستوب لا إغلاق
                    drain_queue(now, which)

    def roll_day(self):
        if today() != self.day:
            self.day, self.day_trades = today(), 0

    # حقول الوقت الأربعة — بوابتان × (منذ / معلّق منذ)
    TS_FIELDS = ("gate_since", "pending_since", "gate_ha_since", "pending_ha_since")

    def save(self):
        d = {k: v for k, v in self.__dict__.items() if k != "last_price"}
        # ① كل حقول الوقت الأربعة تُحوَّل نصاً (كانت اثنتان فقط — وحقلا هيكن
        #    يكسران json.dump فيُفرَّغ الملف وتضيع الصفقات)
        for k in self.TS_FIELDS:
            v = d.get(k)
            d[k] = v.isoformat() if isinstance(v, datetime) else None
        # ② نسخة مستقلة للمراكز — لا نمسّ القاموس الحيّ في الذاكرة
        d["positions"] = {
            t: {**p, "opened_at": p["opened_at"].isoformat()
                     if isinstance(p.get("opened_at"), datetime) else p.get("opened_at")}
            for t, p in self.positions.items()
        }
        # ③ كتابة ذرّية — لو فشلت لا يُفرَّغ الملف القديم
        try:
            tmp = STATE_F + ".tmp"
            with open(tmp, "w") as f: json.dump(d, f, ensure_ascii=False, indent=1)
            os.replace(tmp, STATE_F)
        except Exception as e:
            print("save error:", e, flush=True)

    def load(self):
        if not os.path.exists(STATE_F): return
        try:
            with open(STATE_F) as f: d = json.load(f)
            for k, v in d.items():
                if k in self.TS_FIELDS and v:
                    v = datetime.fromisoformat(v)
                setattr(self, k, v)
            # ④ إرجاع opened_at إلى datetime — كان يبقى نصاً فينكسر أي حساب مدة
            for p in self.positions.values():
                if isinstance(p.get("opened_at"), str):
                    p["opened_at"] = datetime.fromisoformat(p["opened_at"])
        except Exception as e:
            print("load error:", e, flush=True)


ST   = State()
LOCK = threading.Lock()


# ═══════════════════════════════════════════════════════════════
#  🔧 0.8-c — مصالحة المراكز عند الإقلاع
#     يعالج الأشباح المتراكمة قبل هذا الإصدار: أي مركز يثبت الدفتر
#     أن مجموع إغلاقاته ≥ 1.0 يُزال. من بيانات حقيقية لا من تخمين.
# ═══════════════════════════════════════════════════════════════

def reconcile_positions():
    if not ST.positions or not os.path.exists(LEDGER):
        return
    closed = {}          # ticker -> مجموع الأجزاء المغلقة بعد آخر فتح
    try:
        with open(LEDGER) as f:
            for line in f:
                if '"CLOSE"' not in line and '"OPEN"' not in line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                tk = r.get("ticker")
                if not tk:
                    continue
                if r.get("kind") == "OPEN":
                    closed[tk] = 0.0                      # فتح جديد يصفّر العدّاد
                elif r.get("kind") == "CLOSE":
                    closed[tk] = closed.get(tk, 0.0) + float(r.get("portion") or 0)
    except Exception as e:
        print("reconcile read error:", e, flush=True)
        return

    ghosts = [tk for tk in list(ST.positions) if closed.get(tk, 0.0) >= 1.0 - EPS]
    for tk in ghosts:
        ST.positions.pop(tk, None)
        log("reconcile_removed", {"ticker": tk, "closed_portion": closed.get(tk),
                                  "note": "أُغلقت بالكامل في الدفتر وبقيت شبحاً — أُزيلت"})
    if ghosts:
        ST.save()
        log("reconcile_done", {"removed": len(ghosts), "ghosts": ghosts,
                               "remaining": list(ST.positions)})


# ═══════════════════════════════════════════════════════════════
#  الفيتوات
# ═══════════════════════════════════════════════════════════════

def news_blackout(now):
    for when, name in RED_NEWS:
        t = datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        if t - timedelta(hours=24) <= now <= t + timedelta(hours=2):
            return name
    return None

def slots_used(source):
    """عدد المفتوحات المحسوبة على ميزانية بوابة بعينها"""
    return sum(1 for p in ST.positions.values() if p.get("gate_source") == source)

SLOT_CAP = {"ha": SLOT_HA, "raw": SLOT_RAW, "explore": SLOT_EXPLORE}

def vetoes(tk, d, now, which="raw"):
    """يرجع سبب الرفض أو None. الترتيب من الأهم للأقل.
       which = البوابة التي يُطلب الدخول تحت إذنها."""
    if os.path.exists(KILL_FILE):            return "kill_switch"
    if ST.halted:                            return "halted_drawdown"
    n = news_blackout(now)
    if n:                                    return f"news_blackout:{n}"
    g = ST.gate(which)
    if g == 0:                               return "gate_closed"
    if g != d:                               return "against_gate"
    ST.roll_day()
    if ST.day_trades >= MAX_DAILY_TRADES:    return "daily_limit"
    if len(ST.positions) >= MAX_OPEN:        return "max_open"
    # ⭐ الميزانية المستقلة: مقعد شاغر في بوابة لا يُعطى للأخرى
    if slots_used(which) >= SLOT_CAP[which]: return "slots_full_" + which
    if ONE_PER_TICKER and tk in ST.positions: return "already_open"
    return None


# ═══════════════════════════════════════════════════════════════
#  المنفّذ — طبقة منفصلة، تُستبدل بـPionex لاحقاً بلا مساس بالباقي
# ═══════════════════════════════════════════════════════════════

class PaperBroker:
    name = "paper"
    def open(self, tk, side, price):
        return {"ok": True, "fill": price}
    def close(self, tk, side, price, portion):
        return {"ok": True, "fill": price}

BROKER = PaperBroker()


# ═══════════════════════════════════════════════════════════════
#  0.8-e — متابعة الظل تنجو من إعادة النشر
#
#  العطل السابق: threading.Timer بأربع ساعات يعيش في الذاكرة وحدها.
#  أي نشر جديد يمسح كل المؤقتات المعلّقة فتضيع نتائجها نهائياً.
#  وسعر المتابعة كان يُقرأ من آخر تنبيه وصل — فإن لم يصل تنبيه
#  خلال الأربع ساعات فالنتيجة None.
#
#  الإصلاح: طابور على القرص الدائم + عامل يفحصه كل دقيقة +
#  سعر مستقل من بينانس، كما يفعل وكيل التسجيل.
# ═══════════════════════════════════════════════════════════════

def okx_symbol(tk):
    """NEARUSDT.P → NEAR-USDT-SWAP · قاعدة عامة لكل عقود بيونكس الدائمة."""
    u = tk.split(":")[-1].replace("PERP", "").replace(".P", "").strip().upper()
    for q in ("USDT", "USDC", "USD"):
        if u.endswith(q) and len(u) > len(q):
            return f"{u[:-len(q)]}-{q}-SWAP"
    return u


def market_price(tk):
    """
    سعر مستقل — لا يعتمد على وصول تنبيه.

    إصلاح ١٥ أغسطس: بينانس ترد 451 على عناوين Render (مقيسة بـcurl من داخل
    الخدمة)، وبايبت ترد 403. النتيجة كانت shadow_price_error مع كل قيد،
    وكل move_pct فارغ — أي أن دفتر الظل كله بلا قياس.
    البديل: OKX عقود دائمة (200 مؤكدة) ثم binance.vision سبوت احتياطاً.
    ترجع (السعر, اسم المصدر) ليُسجَّل المصدر الفعلي لا اسم ثابت.
    """
    okx = okx_symbol(tk)
    spot = tk.split(":")[-1].replace("PERP", "").replace(".P", "").strip().upper()
    tries = [
        ("okx", f"https://www.okx.com/api/v5/market/ticker?instId={okx}",
         lambda j: j["data"][0]["last"]),
        ("binance.vision",
         f"https://data-api.binance.vision/api/v3/ticker/price?symbol={spot}",
         lambda j: j["price"]),
    ]
    errs = []
    for name, u, pick in tries:
        try:
            req = urllib.request.Request(u, headers={"User-Agent":
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return float(pick(json.load(r))), name
        except Exception as e:
            errs.append(f"{name}:{type(e).__name__}:{str(e)[:40]}")
    log("shadow_price_error", {"ticker": tk, "mapped_okx": okx,
                               "mapped_spot": spot, "errs": errs})
    return None, None


def binance_price(tk):
    """اسم قديم محفوظ للتوافق — يرجع السعر وحده."""
    p, _ = market_price(tk)
    return p


def shadow_queue(tk, d, src, ref_price, ref_ts, mkt,
                 executed=False, reason=None, gh=0, gr=0):
    """يحفظ قيد المتابعة على القرص بدل مؤقّت في الذاكرة"""
    rec = {"tk": tk, "dir": d, "src": src, "ref_price": ref_price,
           "ref_ts": ref_ts, "mkt": mkt, "executed": executed,
           "reason": reason, "gate_ha": gh, "gate_raw": gr,
           "due": (now_utc() + timedelta(minutes=SHADOW_FOLLOW_MIN)).isoformat()}
    try:
        with open(SHADOW_F, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        print("shadow queue error:", e, flush=True)

def shadow_worker():
    """يفحص الطابور كل دقيقة — ينجو من إعادة التشغيل لأن الطابور على القرص"""
    while True:
        try:
            if os.path.exists(SHADOW_F):
                now = now_utc(); keep = []
                rows = []
                with open(SHADOW_F) as f:
                    for l in f:
                        if not l.strip(): continue
                        try: rows.append(json.loads(l))
                        except Exception: pass
                for r in rows:
                    try:
                        due = datetime.fromisoformat(r["due"])
                    except Exception:
                        continue
                    if due > now:
                        keep.append(r); continue
                    p, via = market_price(r["tk"])
                    rp = r.get("ref_price")
                    mv = round((p - rp) / rp * 100 * r["dir"], 3) if (p and rp) else None
                    log("shadow_result", {
                        "ticker": r["tk"], "src": r["src"], "dir": r["dir"],
                        "ref_ts": r["ref_ts"], "ref_price": rp, "price_4h": p,
                        "mkt": r.get("mkt"), "move_pct": mv,
                        "hit": (mv is not None and mv > 0),
                        "executed": r.get("executed"), "reason": r.get("reason"),
                        "gate_ha": r.get("gate_ha"), "gate_raw": r.get("gate_raw"),
                        "via": via or "none"})
                tmp = SHADOW_F + ".tmp"
                with open(tmp, "w") as f:
                    for r in keep:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                os.replace(tmp, SHADOW_F)
        except Exception as e:
            print("shadow worker error:", e, flush=True)
        time.sleep(60)


# ═══════════════════════════════════════════════════════════════
#  الدخول
# ═══════════════════════════════════════════════════════════════

def open_srcs():
    return {p.get("src") for p in ST.positions.values()}

def pick_gate(tk, d, now):
    """
    يرجع (البوابة المختارة، سبب الرفض، هل فيه تعارض).
    التعارض = بوابة تسمح والأخرى تمنع. تُفتح الصفقة وتُسجَّل —
    الحالة المتعارضة أثمن من عشر متفقات، وفيها يظهر الفرق حرفياً.
    """
    res = {w: vetoes(tk, d, now, w) for w in ("ha", "raw")}
    ok  = [w for w in ("ha", "raw") if res[w] is None]
    permits = [w for w in ("ha", "raw") if ST.gate(w) == d]
    conflict = len(permits) == 1
    if ok:
        return ok[0], None, conflict
    # ⭐ المقعد الاستكشافي: البوابتان ممتلئتان لكن إحداهما تأذن،
    #    والإشارة من نوع غير ممثَّل بين المفتوحات = تُؤخذ لتنويع العيّنة قسراً
    return None, (res["ha"] if res["ha"] == res["raw"] else res.get(permits[0]) if permits else res["raw"]), conflict

def try_entry(tk, d, src, price, now):
    which, why, conflict = pick_gate(tk, d, now)

    # ── دفتر الظل: كل إشارة تُسجَّل ولو رُفضت. هذا ما يوسّع العيّنة ×5
    log("shadow", {"ticker": tk, "dir": d, "src": src, "price": price,
                   "gate_ha": ST.gate("ha"), "gate_raw": ST.gate("raw"),
                   "executed": bool(which), "gate_source": which,
                   "conflict": conflict, "reason": why,
                   "mkt": ST.mkt, "mkt_adx": ST.mkt_adx})
    if price:
        # 0.8-e: طابور على القرص بدل مؤقّت يموت مع إعادة النشر.
        # executed/reason يُحفظان مع القيد — بهما يُجاب سؤال
        # «الإشارات التي منعتها البوابة كم منها كان سيربح؟»
        shadow_queue(tk, d, src, price, now.isoformat(), ST.mkt,
                     executed=bool(which), reason=why,
                     gh=ST.gate("ha"), gr=ST.gate("raw"))

    if which is None:
        # ⭐ المقعد الاستكشافي — نوع لم يظهر بين المفتوحات
        for w in ("ha", "raw"):
            if ST.gate(w) == d and src not in open_srcs() \
               and slots_used("explore") < SLOT_EXPLORE \
               and len(ST.positions) < MAX_OPEN \
               and not (ONE_PER_TICKER and tk in ST.positions) \
               and ST.day_trades < MAX_DAILY_TRADES and not ST.halted:
                log("explore_slot", {"ticker": tk, "src": src, "gate": w})
                which, why = "explore", None
                break

    if why:
        # ⭐ الطابور: الرفض بسبب البوابة وحده قابل للاستئناف خلال SIGNAL_TTL_MIN.
        #    لا يتجاوز البوابة — ينتظرها. إن لم تفتح في الوقت، تسقط الإشارة.
        if why in ("gate_closed", "against_gate"):
            QUEUE.append({"tk": tk, "dir": d, "src": src, "price": price, "ts": now})
            log("queued", {"ticker": tk, "dir": d, "src": src, "price": price,
                           "reason": why, "ttl_min": SIGNAL_TTL_MIN,
                           "queue_len": len(QUEUE)})
            return
        # ⭐ الإشارة المكررة على عملة مفتوحة — تُرفض كما كانت، لكن تُوثَّق.
        #    السجل يفرّق لاحقاً بين قاع مزدوج (أعلى + بعد ساعات = تأكيد ضائع)
        #    وسكين هابطة (أدنى + خلال دقائق = الرفض أنقذك).
        if why == "already_open":
            pos = ST.positions.get(tk, {})
            e   = pos.get("entry")
            oa  = pos.get("opened_at")
            gap = None
            try:
                oa_dt = oa if isinstance(oa, datetime) else datetime.fromisoformat(oa)
                gap = round((now - oa_dt).total_seconds() / 60, 1)
            except Exception:
                pass
            delta = None; verdict = "?"
            if e and price:
                # الفارق بمنظور الاتجاه: موجب = الإشارة الثانية أفضل من الدخول
                delta = round((price - e) / e * 100 * d, 3)
                far   = (gap is None or gap >= 60)
                if delta >= 0 and far:      verdict = "تأكيد محتمل (أفضل + بعيد)"
                elif delta < -0.5 and gap is not None and gap < 30:
                    verdict = "⚠️ سكين محتملة (أسوأ + قريب)"
                else:                        verdict = "غامض"
            log("repeat_signal", {"ticker": tk, "dir": d, "src": src,
                                  "sig_price": price, "entry": e,
                                  "delta_pct": delta, "gap_min": gap,
                                  "verdict": verdict, "reason": why})
            return
        log("rejected", {"ticker": tk, "dir": d, "src": src, "reason": why})
        return
    log("armed", {"ticker": tk, "dir": d, "src": src, "price": price,
                  "gate_source": which, "conflict": conflict,
                  "delay_sec": EXEC_DELAY_SEC})
    threading.Timer(EXEC_DELAY_SEC, execute,
                    args=(tk, d, src, price, which, conflict)).start()


def shadow_follow(tk, d, src, ref_price, ref_ts, mkt="?"):
    """
    النسخة القديمة — محفوظة كي لا ينكسر أي مؤقّت ما زال معلّقاً
    من تشغيل سابق. لم تعد تُستدعى في المسار الجديد.
    """
    p = ST.last_price.get(tk, (None, None))[0]
    mv = None
    if p and ref_price:
        mv = round((p - ref_price) / ref_price * 100 * d, 3)
    log("shadow_result", {"ticker": tk, "src": src, "ref_ts": ref_ts,
                          "ref_price": ref_price, "price_4h": p, "mkt": mkt,
                          "move_pct": mv, "hit": (mv is not None and mv > 0),
                          "via": "legacy_timer"})

def execute(tk, d, src, ref_price, which="raw", conflict=False):
    with LOCK:
        now = now_utc()
        why = None if which == "explore" else vetoes(tk, d, now, which)
        if why:
            log("rejected_after_delay", {"ticker": tk, "src": src, "reason": why}); return

        p = ST.last_price.get(tk, (ref_price, now))[0] or ref_price
        # حماية فخ ما بعد الإغلاق: تحرّك ضدك أثناء التأخير = إلغاء
        if ref_price and p:
            move = (p - ref_price) / ref_price * 100 * d
            if move < -ADVERSE_CANCEL:
                log("rejected_after_delay", {"ticker": tk, "src": src,
                    "reason": "adverse_move", "move_pct": round(move, 3)}); return

        r = BROKER.open(tk, d, p)
        if not r.get("ok"):
            log("error", {"ticker": tk, "broker": r}); return

        sl = p * (1 - SL_PCT / 100 / LEVERAGE) if d > 0 else p * (1 + SL_PCT / 100 / LEVERAGE)
        ST.positions[tk] = {"side": d, "entry": p, "sl": sl, "src": src,
                            "half": False, "peak": p, "opened_at": now.isoformat(),
                            "gate_source": which, "conflict": conflict}
        ST.day_trades += 1
        log("OPEN", {"ticker": tk, "dir": "LONG" if d > 0 else "SHORT", "src": src,
                     "entry": p, "sl": round(sl, 6), "margin": MARGIN_USD, "lev": LEVERAGE,
                     "gate_source": which, "conflict": conflict,
                     "slots": {w: slots_used(w) for w in ("ha", "raw", "explore")}})
        ST.save()


# ═══════════════════════════════════════════════════════════════
#  الطابور — إشارات سبقت البوابة بدقائق
# ═══════════════════════════════════════════════════════════════

QUEUE = []   # [{tk, dir, src, price, ts}]  — في الذاكرة، عمرها دقائق

def drain_queue(now, which="raw"):
    """
    يُستدعى لحظة فتح البوابة أو انقلابها.
    لا يتجاوز البوابة إطلاقاً — ينفّذ ما يوافق اتجاهها فقط،
    وما زال داخل مهلة SIGNAL_TTL_MIN. الباقي يسقط.
    """
    global QUEUE
    if not QUEUE:
        return
    kept, fired, expired, wrong = [], 0, 0, 0
    # الأحدث أولاً — الأقرب للسعر الحالي أصدق
    for s in sorted(QUEUE, key=lambda x: x["ts"], reverse=True):
        age_min = (now - s["ts"]).total_seconds() / 60
        if age_min > SIGNAL_TTL_MIN:
            expired += 1; continue
        if s["dir"] != ST.gate(which):
            wrong += 1; continue
        why = vetoes(s["tk"], s["dir"], now, which)
        if why:
            # ما زال ممنوعاً لسبب آخر (حد يومي/مفتوحة) — يبقى في الطابور
            if why in ("gate_closed", "against_gate"):
                kept.append(s)
            else:
                log("queue_dropped", {"ticker": s["tk"], "src": s["src"],
                                      "reason": why, "age_min": round(age_min, 1)})
            continue
        log("queue_fired", {"ticker": s["tk"], "dir": s["dir"], "src": s["src"],
                            "price": s["price"], "age_min": round(age_min, 1)})
        try_entry(s["tk"], s["dir"], s["src"], s["price"], now)
        fired += 1
    QUEUE = kept
    log("queue_drain", {"gate": which, "fired": fired, "expired": expired,
                        "wrong_dir": wrong, "remaining": len(QUEUE)})


# ═══════════════════════════════════════════════════════════════
#  الخروج — قاعدتك المعتمدة 31 يوليو، ثلاث مراحل
# ═══════════════════════════════════════════════════════════════

def pnl_pct(pos, price):
    """الربح كنسبة من الهامش (مع الرافعة)"""
    return (price - pos["entry"]) / pos["entry"] * 100 * LEVERAGE * pos["side"]

def tp_price(pos):
    """السعر الذي يتحقق عنده الهدف بالضبط — أمر محدَّد يُنفَّذ عنده لا فوقه"""
    return pos["entry"] * (1 + pos["side"] * TP_PCT / (100.0 * LEVERAGE))

def close_position(tk, portion, reason, price, feed_price=None):
    pos = ST.positions.get(tk)
    if not pos: return
    pl = pnl_pct(pos, price) * portion
    BROKER.close(tk, pos["side"], price, portion)
    ST.balance += MARGIN_USD * pl / 100
    ST.peak = max(ST.peak, ST.balance)

    # ── مدة الصفقة بالدقائق (للتحليل النهائي)
    dur = None
    try:
        oa = pos.get("opened_at")
        oa_dt = oa if isinstance(oa, datetime) else datetime.fromisoformat(oa)
        dur = round((now_utc() - oa_dt).total_seconds() / 60, 1)
    except Exception:
        pass

    # ── 0.8-c: سجل مُثرى — بدون gate_source لا يمكن حسم قاعدة البوابتين
    #    0.8-d: price = سعر التنفيذ الفعلي (الستوب/الهدف)، feed_price = السعر الواصل
    log("CLOSE", {"ticker": tk, "portion": portion, "reason": reason,
                  "price": price, "feed_price": feed_price,
                  "feed_gap_pct": (round((feed_price - price) / price * 100, 3)
                                   if feed_price and price else None),
                  "pnl_pct": round(pl, 1),
                  "balance": round(ST.balance, 3),
                  "entry": pos.get("entry"),
                  "side": "LONG" if pos.get("side", 0) > 0 else "SHORT",
                  "src": pos.get("src"),
                  "gate_source": pos.get("gate_source"),
                  "conflict": pos.get("conflict"),
                  "was_half": bool(pos.get("half")),
                  "duration_min": dur,
                  "mkt": ST.mkt})

    # ── 🔴 الإصلاح الجوهري 0.8-c
    #    كان: if portion >= 1.0 — فالنصف الثاني يُغلق محاسبياً
    #    وتبقى الصفقة في القائمة للأبد، فتمتلئ المقاعد بموتى.
    #    الآن: النصف الثاني (half=True) يُزيلها أيضاً.
    if portion >= 1.0 - EPS or pos.get("half"):
        ST.positions.pop(tk, None)
        log("position_removed", {"ticker": tk, "reason": reason,
                                 "slots": {w: slots_used(w) for w in ("ha", "raw", "explore")}})

    # حد التراجع
    if ST.peak > 0 and (ST.peak - ST.balance) / ST.peak * 100 >= MAX_DRAWDOWN_PCT:
        ST.halted = True
        log("HALT", {"reason": "max_drawdown", "balance": round(ST.balance, 2)})
    ST.save()

def on_price(tk, price, now):
    """يُستدعى مع كل تنبيه يحمل سعراً — يفحص المراحل الثلاث"""
    ST.last_price[tk] = (price, now)
    pos = ST.positions.get(tk)
    if not pos: return
    d = pos["side"]
    pos["peak"] = max(pos["peak"], price) if d > 0 else min(pos["peak"], price)

    # ── الستوب أولاً دائماً
    #    🔴 0.8-d: يُنفَّذ عند سعر الستوب لا عند السعر الواصل.
    #    الوكيل يستقبل الأسعار مع التنبيهات فقط، فقد يصل سعر أبعد
    #    بكثير من الستوب. حسابه كسعر تنفيذ يخترع خسارة لم تقع:
    #    breakeven_stop سجّل 90 خسارة من 90 بمتوسط −26% —
    #    وستوبه على نقطة الدخول بالضبط، أي أن الصحيح صفر.
    if (d > 0 and price <= pos["sl"]) or (d < 0 and price >= pos["sl"]):
        close_position(tk, 1.0 if not pos["half"] else 0.5,
                       "breakeven_stop" if pos["half"] else "stop_loss",
                       pos["sl"], feed_price=price)
        return

    # ── المرحلة 1+2: بلوغ الهدف = أغلق النصف وانقل الستوب لنقطة الدخول
    #    0.8-c: هامش EPS — حركة 2% × 25x تعطي 49.9999999999997 فتسقط بلا سببه
    #    0.8-d: التنفيذ عند سعر الهدف — الأمر المحدَّد يُملأ عنده لا فوقه
    if not pos["half"] and pnl_pct(pos, price) >= TP_PCT - EPS:
        close_position(tk, 0.5, "TP_half", tp_price(pos), feed_price=price)
        if tk in ST.positions:
            ST.positions[tk]["half"] = True
            ST.positions[tk]["sl"]   = pos["entry"]        # ← breakeven
            log("BREAKEVEN", {"ticker": tk, "sl": pos["entry"],
                              "note": "ممنوع تحريكه للأسفل بعد الآن"})
            ST.save()

def on_exit_signal(role, now, price_map):
    """
    exit_top → يغلق اللونجات   |   exit_bot → يغلق الشورتات
    (السلك المفقود: كل إشارة تقول افتح شورت تقول أيضاً أغلق اللونج)

    🔴 0.8-g: الحارس `if not pos["half"]` أُزيل.
       كان يرمي الإشارة كاملة إن لم تبلغ الصفقة هدفها — 543 إشارة
       مرمية من 891 (61%). والصفقة التي لم تربح شيئاً كانت محرومة
       من كل حماية عدا الستوب الأصلي، وهي الأحوج للحماية.
       قاعدة 31 يوليو: المرحلة 3 لا تشترط المرحلة 1.

    🔴 والنسبة صارت مشروطة (نفس صيغة الستوب في on_price):
       1.0 للصفقة الكاملة · 0.5 لما تبقّى بعد TP.
       0.5 الثابتة القديمة كانت ستغلق نصف صفقة كاملة ولا تُزيلها
       (شرط 0.8-c يتطلب portion≥1.0 أو half) = عودة الصفقة الشبح.
    """
    want = +1 if role == "exit_top" else -1
    for tk, pos in list(ST.positions.items()):
        if pos["side"] != want: continue
        p = price_map.get(tk) or ST.last_price.get(tk, (pos["entry"],))[0]
        close_position(tk, 1.0 if not pos["half"] else 0.5,
                       f"exit_signal:{role}", p)

def on_gate_flip(new_dir):
    """
    ⭐ انقلاب البوابة لا يغلق شيئاً — يشدّ الستوب لنقطة الدخول فقط.
    السبب: تذبذب البوابة (فتح·قفل·فتح) كان يذبح الصفقات عند نقاط عشوائية.
    الصفقة بعد فتحها تُدار بشروطها هي: الستوب · الهدف · إشارات القمة/القاع.
    والبوابة المنقلبة تمنع الدخول الجديد فقط.
    ⚠️ الستوب لا يُحرَّك للأسفل أبداً — إن كان أقرب من الدخول يبقى مكانه.
    """
    for tk, pos in list(ST.positions.items()):
        if pos["side"] == new_dir:
            continue
        old_sl, entry, d = pos["sl"], pos["entry"], pos["side"]
        # الشدّ باتجاه واحد فقط: نحو الدخول، لا بعيداً عنه
        new_sl = max(old_sl, entry) if d > 0 else min(old_sl, entry)
        if new_sl != old_sl:
            pos["sl"] = new_sl
            log("gate_flip_breakeven", {"ticker": tk, "old_sl": round(old_sl, 6),
                "new_sl": round(new_sl, 6), "note": "انقلاب البوابة — شدّ لا إغلاق"})
        else:
            log("gate_flip_hold", {"ticker": tk, "sl": round(old_sl, 6),
                "note": "الستوب أضيق من الدخول أصلاً — بلا تغيير"})
    ST.save()


# ═══════════════════════════════════════════════════════════════
#  استقبال الويبهوك
# ═══════════════════════════════════════════════════════════════

def parse_extras(msg):
    """يستخرج | interval | ticker | close  إن أُضيفت لنص التنبيه"""
    tf = tk = None; px = None
    parts = [p.strip() for p in msg.split("|")]
    for p in parts[1:]:
        # الفريم: رقم قصير (5/15/60/240) أو 1D/4h — أربع خانات كحد أقصى
        if tf is None and re.fullmatch(r"\d{1,4}|1[DdWw]|\d{1,2}[hmHM]", p):
            tf = p.lower(); continue
        if tk is None and re.fullmatch(r"[A-Za-z0-9:._]{4,}", p) and not p.replace(".", "").isdigit():
            tk = p; continue
        try: px = float(p.replace(",", ""))
        except: pass
    if tk is None:
        m = re.search(r"(?:@|on|على)\s*([A-Z0-9:._]{4,})", msg)
        if m: tk = m.group(1)
    if px is None:
        m = re.search(r"\b(\d{2,}\.?\d*)\b", parts[-1]) if len(parts) > 1 else None
        if m:
            try: px = float(m.group(1))
            except: pass
    return tf, tk, px

def handle(msg):
    now = now_utc()
    ST.check_pending(now)
    role, d, src = classify(msg)
    tf, tk, px = parse_extras(msg)
    tk = (tk or "BTCUSDT.P").replace("BINANCE:", "")

    base = {"msg": msg[:180], "role": role, "src": src, "dir": d,
            "tf": tf, "ticker": tk, "price": px}

    if role is None:
        log("ignored", {**base, "reason": "لم يُصنَّف"}); return

    # حماية الفريم — يكشف ربط الرابط بالنسخة الخطأ بدل تنفيذه
    exp = EXPECTED_TF.get(src)
    if exp and tf and tf not in exp:
        log("rejected", {**base, "reason": f"فريم خاطئ (المتوقع {exp})"}); return

    # ── حالة السوق: تُخزَّن ولا تفتح صفقة
    if role == "mkt":
        import re as _re
        a = _re.search(r"ADX\s*([0-9.]+)", msg)
        with LOCK:
            ST.mkt     = "UP" if d == 1 else "DOWN" if d == -1 else "RANGE"
            ST.mkt_adx = float(a.group(1)) if a else None
            ST.mkt_ts  = now.isoformat()
            ST.save()
        log("market_state", {**base, "mkt": ST.mkt, "adx": ST.mkt_adx}); return

    if px: on_price(tk, px, now)

    with LOCK:
        if role in ("gate_ha", "gate_raw"):
            which = role.split("_")[1]
            if d == 0:
                prev = ST.set_neutral(now, which)
                ST.save()
                log("gate_neutral", {**base, "gate": which, "prev_gate": prev,
                                     "gate_ha": ST.gate("ha"), "gate_raw": ST.gate("raw"),
                                     "open_positions": list(ST.positions),
                                     "queued": len(QUEUE),
                                     "note": "منع دخول جديد — الصفقات المفتوحة تُدار بشروطها"})
            else:
                r = ST.set_gate(d, now, which)
                log("gate", {**base, "gate": which, "result": r,
                             "gate_ha": ST.gate("ha"), "gate_raw": ST.gate("raw"),
                             "conflict": ST.gate("ha") != ST.gate("raw")})
                if r == "flip": on_gate_flip(d)
                if r in ("open", "flip"): drain_queue(now, which)
                ST.save()

        elif role in ("exit_top", "exit_bot"):
            log("exit_signal", base)
            on_exit_signal(role, now, {tk: px} if px else {})

        elif role == "veto":
            log("veto_state", base)

        elif role == "entry":
            if not px:
                log("rejected", {**base, "reason": "بلا سعر — أضف {{close}} للرسالة"}); return
            try_entry(tk, d, src, px, now)


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        if SECRET and SECRET not in self.path:
            log("bad_path", {"path": self.path[:60]})
            self.send_response(403); self.end_headers(); return
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode("utf-8", "ignore")
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        log("received", {"len": len(body), "head": body[:70]})
        try:
            handle(body)
        except Exception as e:
            log("error", {"exc": str(e), "body": body[:200]})

    def _send_json(self, obj):
        out = json.dumps(obj, ensure_ascii=False, indent=1).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers(); self.wfile.write(out)

    def do_GET(self):
        # ── 0.8-c: مسار الصفقات المكتملة — للحكم يوم 21 أغسطس
        if SECRET and self.path.startswith("/trades") and SECRET in self.path:
            self._send_json(trades_summary()); return

        # ── 0.8-e: ملخّص الممنوع — كم من الإشارات التي منعتها البوابة كان سيربح
        if SECRET and self.path.startswith("/blocked") and SECRET in self.path:
            self._send_json(blocked_summary()); return

        # ── 0.8-e: تصدير دفتر الظل الخام
        #    /ledger/SECRET                      = آخر 3000 سطر
        #    /ledger/SECRET?kind=shadow_result   = نوع واحد فقط
        if SECRET and self.path.startswith("/ledger") and SECRET in self.path:
            kinds = None
            m = re.search(r"kind=([A-Za-z_,]+)", self.path)
            if m: kinds = set(m.group(1).split(","))
            out = []
            try:
                with open(LEDGER) as f:
                    for l in f:
                        if not l.strip(): continue
                        try: r = json.loads(l)
                        except Exception: continue
                        if kinds and r.get("kind") not in kinds: continue
                        out.append(r)
            except Exception as e:
                out = [{"error": str(e)}]
            self._send_json(out[-3000:]); return

        # ── إجمالي الأحداث = كل أسطر الدفتر، لا الـ25 المعروضة فقط
        tail = []; total = 0
        try:
            with open(LEDGER) as f:
                lines = f.readlines()
            total = len(lines)
            for l in lines[-25:]:
                r = json.loads(l)
                tail.append(f"{r['ts'][11:19]} · {r['kind']} · "
                            f"{r.get('ticker') or r.get('src') or ''} "
                            f"{r.get('reason') or ''}".strip())
        except Exception:
            pass
        if not tail:
            tail = ["لا توجد أحداث بعد"]
        pend = 0
        try:
            if os.path.exists(SHADOW_F):
                with open(SHADOW_F) as f:
                    pend = sum(1 for l in f if l.strip())
        except Exception:
            pass
        body = {
            "الإصدار": CONFIG_VERSION,
            "حالة السوق": f"{ST.mkt}" + (f" · ADX {ST.mkt_adx}" if ST.mkt_adx else ""),
            "الحالة": "ورقي" if PAPER_MODE else "تنفيذ حقيقي",
            "بوابة هيكن": {1: "LONG", -1: "SHORT", 0: "مقفولة"}.get(ST.gate("ha")),
            "بوابة الخام": {1: "LONG", -1: "SHORT", 0: "مقفولة"}.get(ST.gate("raw")),
            "تعارض البوابتين": ST.gate("ha") != ST.gate("raw"),
            "المقاعد": {w: f"{slots_used(w)}/{SLOT_CAP[w]}" for w in ("ha", "raw", "explore")},
            "معلّق": ST.pending_dir, "صفقات مفتوحة": list(ST.positions),
            "صفقات اليوم": ST.day_trades, "الرصيد": round(ST.balance, 3),
            "متوقف": ST.halted, "إجمالي الأحداث": total,
            "التخزين": "💾 دائم" if DATA_DIR != BASE else "⚠️ مؤقت",
            "الطابور": len(QUEUE),
            "ظل ينتظر المتابعة": pend,
            "آخر الأحداث": tail[::-1],
        }
        self._send_json(body)
    def log_message(self, *a): pass


# ═══════════════════════════════════════════════════════════════
#  ملخّص الصفقات — 0.8-c · للحكم النهائي
# ═══════════════════════════════════════════════════════════════

def trades_summary():
    """يجمع كل CLOSE من الدفتر ويقسّمها حسب البوابة والمصدر والنتيجة."""
    if not os.path.exists(LEDGER):
        return {"error": "لا يوجد دفتر"}
    rows = []
    with open(LEDGER) as f:
        for line in f:
            if '"CLOSE"' not in line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") == "CLOSE":
                rows.append(r)

    def bucket(key_fn):
        out = {}
        for r in rows:
            k = key_fn(r) or "?"
            b = out.setdefault(k, {"عدد": 0, "رابحة": 0, "خاسرة": 0, "مجموع%": 0.0})
            p = float(r.get("pnl_pct") or 0)
            b["عدد"] += 1
            b["رابحة" if p > 0 else "خاسرة"] += 1
            b["مجموع%"] = round(b["مجموع%"] + p, 1)
        for b in out.values():
            b["نسبة الربح%"] = round(b["رابحة"] / b["عدد"] * 100, 1) if b["عدد"] else 0
            b["متوسط%"] = round(b["مجموع%"] / b["عدد"], 1) if b["عدد"] else 0
        return out

    wins = sum(1 for r in rows if float(r.get("pnl_pct") or 0) > 0)
    return {
        "إجمالي الإغلاقات": len(rows),
        "رابحة": wins, "خاسرة": len(rows) - wins,
        "نسبة الربح%": round(wins / len(rows) * 100, 1) if rows else 0,
        "حسب البوابة": bucket(lambda r: r.get("gate_source")),
        "حسب المصدر": bucket(lambda r: r.get("src")),
        "حسب السبب": bucket(lambda r: r.get("reason")),
        "حسب الإصدار": bucket(lambda r: r.get("cfg")),
        "الرصيد الحالي": round(ST.balance, 3),
    }


# ═══════════════════════════════════════════════════════════════
#  ملخّص الممنوع — 0.8-e
#  السؤال الذي لم يُطرح قط: الإشارات التي منعتها البوابة،
#  كم منها كان سيربح؟ هذا نصف معيار الاستبعاد (التعطيل).
# ═══════════════════════════════════════════════════════════════

def blocked_summary():
    if not os.path.exists(LEDGER):
        return {"error": "لا يوجد دفتر"}
    rows = []
    with open(LEDGER) as f:
        for line in f:
            if '"shadow_result"' not in line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") == "shadow_result" and r.get("move_pct") is not None:
                rows.append(r)

    def bucket(key_fn):
        out = {}
        for r in rows:
            k = key_fn(r)
            if k is None:
                continue
            b = out.setdefault(str(k), {"عدد": 0, "صدقت": 0, "مجموع%": 0.0})
            b["عدد"] += 1
            if r.get("hit"):
                b["صدقت"] += 1
            b["مجموع%"] = round(b["مجموع%"] + float(r["move_pct"]), 1)
        for b in out.values():
            b["نسبة الصدق%"] = round(b["صدقت"] / b["عدد"] * 100, 1) if b["عدد"] else 0
            b["متوسط%"] = round(b["مجموع%"] / b["عدد"], 3) if b["عدد"] else 0
        return out

    def agg(lst):
        if not lst:
            return {"عدد": 0}
        h = sum(1 for r in lst if r.get("hit"))
        s = sum(float(r["move_pct"]) for r in lst)
        return {"عدد": len(lst), "صدقت": h,
                "نسبة الصدق%": round(h / len(lst) * 100, 1),
                "متوسط%": round(s / len(lst), 3)}

    blocked = [r for r in rows if r.get("executed") is False]
    done    = [r for r in rows if r.get("executed") is True]
    return {
        "قيود لها نتيجة": len(rows),
        "الممنوعة": agg(blocked),
        "المنفَّذة": agg(done),
        "الممنوعة حسب السبب": bucket(
            lambda r: r.get("reason") if r.get("executed") is False else None),
        "حسب المصدر": bucket(lambda r: r.get("src") or "?"),
        "حسب حالة السوق": bucket(lambda r: r.get("mkt") or "?"),
        "ملاحظة": "القيود قبل 0.8-e بلا executed/reason — لا تدخل التقسيم",
    }


# ═══════════════════════════════════════════════════════════════
#  التقرير اليومي
# ═══════════════════════════════════════════════════════════════

def report():
    if not os.path.exists(LEDGER):
        print("لا يوجد سجل بعد."); return
    rows = [json.loads(l) for l in open(LEDGER) if l.strip()]
    day  = today()
    d    = [r for r in rows if r["ts"][:10] == day]
    cnt  = lambda k: sum(1 for r in d if r["kind"] == k)
    print(f"\n═══ تقرير {day} ═══")
    print(f"إشارات واردة : {len(d)}")
    print(f"صفقات مفتوحة : {cnt('OPEN')}")
    print(f"إغلاقات      : {cnt('CLOSE')}")
    print(f"مرفوضة       : {cnt('rejected') + cnt('rejected_after_delay')}")
    reasons = {}
    for r in d:
        if r["kind"].startswith("rejected"):
            reasons[r.get("reason", "?")] = reasons.get(r.get("reason", "?"), 0) + 1
    if reasons:
        print("\nأسباب الرفض (دفتر الظل):")
        for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {v:>3} × {k}")
    print(f"\nالبوابة: {ST.gate_dir}  |  الرصيد: {ST.balance:.3f}  |  متوقف: {ST.halted}")
    print("═" * 30)


if __name__ == "__main__":
    if "--report" in sys.argv:
        report(); sys.exit(0)
    print("═" * 55)
    print(f"  وكيل محمود {CONFIG_VERSION}  |  {'📝 ورقي' if PAPER_MODE else '⚠️ تنفيذ حقيقي'}")
    print(f"  المنفذ {PORT}  |  المسار: /{SECRET}")
    print(f"  البيانات: {DATA_DIR}  {'💾 دائم' if DATA_DIR != BASE else '⚠️ مؤقت — تُمسح عند إعادة النشر'}")
    print(f"  إيقاف فوري: أنشئ ملف {KILL_FILE}")
    print("═" * 55)
    reconcile_positions()          # 0.8-c — تنظيف الأشباح من بيانات الدفتر
    threading.Thread(target=shadow_worker, daemon=True).start()
    print("🔄 عامل متابعة الظل بدأ — طابور على القرص، سعر من بينانس", flush=True)
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()
