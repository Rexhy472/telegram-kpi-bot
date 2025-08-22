import os, re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

# ===================== Helpers =====================
def parse_amount(text: str) -> int:
    if text is None: return 0
    cleaned = re.sub(r"[^\d-]", "", str(text))
    if cleaned in ("", "-"): return 0
    try: return int(cleaned)
    except Exception: return 0

def fmt_id(num) -> str:
    try: return f"{int(num):,}".replace(",", ".")
    except Exception: return str(num or "")

def valid_tanggal(s: str) -> bool:
    try:
        datetime.strptime(s, "%d/%m/%Y")
        return True
    except Exception:
        return False

def get_laporan(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if 'laporan' not in context.user_data:
        context.user_data['laporan'] = {}
    return context.user_data['laporan']

def shift2digits(s: str) -> str:
    try: return f"{int(s):02d}"
    except Exception: return str(s or "01")

def reply_kb():
    # Tombol permanen di dekat tombol emoji
    return ReplyKeyboardMarkup([["/start", "/help", "/preview", "/batal"]], resize_keyboard=True)

def ensure_defaults_for_shift(d: dict, shift: str):
    s = "1" if str(shift) == "1" else "2"
    for key in [f"tertib_setor_shift{s}", f"store_activity_shift{s}", f"kbk_shift{s}", f"pjr_shift{s}", f"itt_shift{s}"]:
        if not d.get(key): d[key] = "✅"

def ensure_defaults_for_both_shifts(d: dict):
    for s in ("1", "2"):
        for key in [f"tertib_setor_shift{s}", f"store_activity_shift{s}", f"kbk_shift{s}", f"pjr_shift{s}", f"itt_shift{s}"]:
            if not d.get(key): d[key] = "✅"

# ===================== Renderer (template panjang) =====================
def render_report(d: dict) -> str:
    store = d.get('store', "T67T CIBULARENG")
    kpi_title = d.get('kpi_title', "KPI")
    shift = shift2digits(d.get('shift', '1'))
    tanggal = d.get('tanggal') or datetime.now().strftime("%d/%m/%Y")

    total_sales = d.get('total_sales', "")
    sales_str = fmt_id(total_sales) if isinstance(total_sales, int) else str(total_sales or "")
    total_struk = d.get('total_struk', "")

    mrbread     = fmt_id(d.get('mrbread', "")) if d.get('mrbread', "") != "" else ""
    primebread  = fmt_id(d.get('primebread', "")) if d.get('primebread', "") != "" else ""
    telur       = fmt_id(d.get('telur', "")) if d.get('telur', "") != "" else ""
    buah_import = fmt_id(d.get('buah_import', "")) if d.get('buah_import', "") != "" else ""
    buah_lokal  = fmt_id(d.get('buah_lokal', "")) if d.get('buah_lokal', "") != "" else ""
    all_produk_v = d.get('all_produk', "")
    all_produk  = fmt_id(all_produk_v) if all_produk_v not in ("", None) else ""

    v1i = d.get('variance_shift1_induk', "")
    v1a = d.get('variance_shift1_anak', "")
    v2i = d.get('variance_shift2_induk', "")
    v2a = d.get('variance_shift2_anak', "")
    variance_poin = d.get('variance_poin', "5")
    variance_plus_gt10k = d.get('variance_plus_total_gt10k', "0")

    cancel_poin  = d.get('cancel_poin', "5")
    cancel_budget = d.get('cancel_budget', "")
    cancel_shift1 = d.get('cancel_shift1', "")
    cancel_shift2 = d.get('cancel_shift2', "")
    cancel_total  = d.get('cancel_total', "0")

    tertib_poin  = d.get('tertib_poin', "5")
    tertib_s1    = d.get('tertib_setor_shift1', "")
    tertib_s2    = d.get('tertib_setor_shift2', "")

    cpu_50_left  = d.get('cpu_50_left', "50 %")
    cpu_50_right = d.get('cpu_50_right', "50 %")
    cpu_s1_induk = d.get('trx_cpu_shift1_induk', "")
    cpu_s1_anak  = d.get('trx_cpu_shift1_anak', "")
    cpu_s2_induk = d.get('trx_cpu_shift2_induk', "")
    cpu_s2_anak  = d.get('trx_cpu_shift2_anak', "")

    tunai_poin   = d.get('tunai_poin', "5")
    tunai_target = d.get('tunai_target', "215")
    tunai_s1     = d.get('tunai_shift1', "")
    tunai_s2     = d.get('tunai_shift2', "")
    tunai_total  = d.get('tunai_total', "")
    tunai_sisa   = d.get('tunai_sisa', "")

    isaku_poin   = d.get('isaku_poin', "5")
    isaku_target = d.get('isaku_target', "8")
    isaku_s1     = d.get('isaku_shift1', "")
    isaku_s2     = d.get('isaku_shift2', "")
    isaku_total  = d.get('isaku_total', "")
    isaku_sisa   = d.get('isaku_sisa', "")

    poinku_poin   = d.get('poinku_poin', "10")
    poinku_target = d.get('poinku_target', "10")
    poinku_s1     = d.get('poinku_shift1', "")
    poinku_s2     = d.get('poinku_shift2', "")
    poinku_total  = d.get('poinku_total', "")
    poinku_sisa   = d.get('poinku_sisa', "")

    klik_poin   = d.get('klik_poin', "10")
    klik_target = d.get('klik_target', "13")
    klik_s1     = d.get('klik_shift1', "")
    klik_s2     = d.get('klik_shift2', "")
    klik_total  = d.get('klik_total', "")
    klik_sisa   = d.get('klik_sisa', "")

    store_act_s1 = d.get('store_activity_shift1', "")
    store_act_s2 = d.get('store_activity_shift2', "")
    kbk_poin = d.get('kbk_poin', "5")
    kbk_s1   = d.get('kbk_shift1', "")
    kbk_s2   = d.get('kbk_shift2', "")
    kbk_total = d.get('kbk_total', "5")
    kbk_sisa  = d.get('kbk_sisa', "")
    pjr_poin   = d.get('pjr_poin', "10")
    pjr_target = d.get('pjr_target', "")
    pjr_s1     = d.get('pjr_shift1', "")
    pjr_s2     = d.get('pjr_shift2', "")
    itt_poin   = d.get('itt_poin', "5")
    itt_budget = d.get('itt_budget', "")
    itt_s1     = d.get('itt_shift1', "")
    itt_s2     = d.get('itt_shift2', "")
    itt_total  = d.get('itt_total', "")

    varmin_total = d.get('total_varmin', "0")
    varmin_dian  = d.get('varmin_dian', "0")
    varmin_dinda = d.get('varmin_dinda', "0")
    varmin_agung = d.get('varmin_agung', "0")
    varmin_rifa  = d.get('varmin_rifa', "0")
    varmin_putri = d.get('varmin_putri', "0")
    varplus_total = d.get('total_varplus', "")
    varplus_dian  = d.get('variance_plus_dian', "")
    varplus_dinda = d.get('variance_plus_dinda', "")
    varplus_agung = d.get('variance_plus_agung', "")
    varplus_rifa  = d.get('variance_plus_rifa', "")
    varplus_putri = d.get('variance_plus_putri', "")

    lines = []
    lines.append(f"*{store}*")
    lines.append(f"Monitoring *{kpi_title}* ")
    lines.append(f" SHIFT {shift}")
    lines.append(f"Tanggal: {tanggal}\n")
    lines.append(f"Sales: {sales_str}")
    lines.append(f"Struk : {total_struk}\n")
    lines.append(f"*Sales produk khusus*")
    lines.append(f"Mr.bread: {mrbread}")
    lines.append(f"Prime bread: {primebread}")
    lines.append(f"Telur : {telur}")
    lines.append(f"Buah Import : {buah_import}")
    lines.append(f"Buah lokal : {buah_lokal}")
    lines.append(f"All Produk : {all_produk}\n")
    lines.append(f"*VARIANCE*")
    lines.append(f"POIN {variance_poin}")
    lines.append("Budget")
    lines.append("Shift 1")
    lines.append(f"Induk : {v1i}")
    lines.append(f"Anak : {v1a}\n")
    lines.append("Shift 2")
    lines.append(f"Induk  : {v2i}")
    lines.append(f"Anak : {v2a}\n")
    lines.append(f"Total Variance Plus di atas Rp.10.000 : {variance_plus_gt10k}\n")
    lines.append(f"*CANCEL SALES*")
    lines.append(f"POIN {cancel_poin}")
    lines.append(f"Budget : {cancel_budget}")
    lines.append(f"Shift 1 : {cancel_shift1}")
    lines.append(f"Shift 2 : {cancel_shift2}")
    lines.append(f"Total cancel : {cancel_total}\n")
    lines.append(f"*TERTIB SETOR*")
    lines.append(f"POIN {tertib_poin}")
    lines.append(f"Shift 1 : {tertib_s1}")
    lines.append(f"Shift 2 : {tertib_s2}\n")
    lines.append(f"*JMLH TRX CPU*")
    lines.append(f"{cpu_50_left} : {cpu_50_right}")
    lines.append("Shift 1")
    lines.append(f"Induk : {cpu_s1_induk}")
    lines.append(f"Anak : {cpu_s1_anak}\n")
    lines.append("Shift 2")
    lines.append(f"Induk : {cpu_s2_induk}")
    lines.append(f"Anak : {cpu_s2_anak}\n")
    lines.append(f"*JMLH TRX TUNAI*")
    lines.append(f"POIN {tunai_poin}")
    lines.append(f"Target : {tunai_target}")
    lines.append(f"Shift 1 : {tunai_s1}")
    lines.append(f"Shift 2 : {tunai_s2}")
    lines.append(f"Total trx tunai : {tunai_total}")
    lines.append(f"Sisa : {tunai_sisa}\n")
    lines.append(f"*NEW MEMBER ISAKU*")
    lines.append(f"POIN {isaku_poin}")
    lines.append(f"Target : {isaku_target}")
    lines.append(f"Shift 1 : {isaku_s1}")
    lines.append(f"Shift 2 : {isaku_s2}")
    lines.append(f"Total  : {isaku_total}")
    lines.append(f"Sisa : {isaku_sisa}\n")
    lines.append(f"*NEW MEMBER POINKU*")
    lines.append(f"POIN {poinku_poin}")
    lines.append(f"Target : {poinku_target}")
    lines.append(f"Shift 1 : {poinku_s1}")
    lines.append(f"Shift 2 : {poinku_s2}")
    lines.append(f"Total : {poinku_total}")
    lines.append(f"Sisa : {poinku_sisa}\n")
    lines.append(f"*NEW MEMBER KLIK*")
    lines.append(f"POIN {klik_poin}")
    lines.append(f"Target : {klik_target}")
    lines.append(f"Shift 1 : {klik_s1}")
    lines.append(f"Shift 2 : {klik_s2}")
    lines.append(f"Total : {klik_total}")
    lines.append(f"Sisa : {klik_sisa}\n")
    lines.append(f"*STORE ACTIVITY*")
    lines.append("Poin 5")
    lines.append(f"Shift 1 : {store_act_s1} ")
    lines.append(f"Shift 2 : {store_act_s2}\n")
    lines.append(f"*TOKO PRIMA/KBK*")
    lines.append(f"POIN {kbk_poin}")
    lines.append(f"Shift 1 : {kbk_s1}")
    lines.append(f"Shift 2 : {kbk_s2}")
    lines.append(f"Total : {kbk_total}")
    lines.append(f"Sisa : {kbk_sisa}\n")
    lines.append(f"*PELAKSANAAN  PJR(scan itt)*")
    lines.append(f"Target : {pjr_target}")
    lines.append(f"POIN {pjr_poin}")
    lines.append("Target")
    lines.append(f"Shift 1 : {pjr_s1}")
    lines.append(f"Shift 2 : {pjr_s2}\n")
    lines.append(f"*QTY ITT*")
    lines.append(f"POIN {itt_poin}")
    lines.append(f"Budget : {itt_budget}")
    lines.append(f"Shift 1 : {itt_s1}")
    lines.append(f"Shift 2 : {itt_s2}")
    lines.append(f"Total itt : {itt_total}\n")
    lines.append(f"*TARGET POIN 100*\n")
    lines.append(f"*Akumulasi varian mines*")
    lines.append(f"Total varmin : {varmin_total}")
    lines.append(f"Dian : {varmin_dian}")
    lines.append(f"Dinda : {varmin_dinda}")
    lines.append(f"Agung : {varmin_agung}")
    lines.append(f"Rifa : {varmin_rifa}")
    lines.append(f"Putri : {varmin_putri}\n")
    lines.append(f"*Akumulasi variance plus*")
    lines.append(f"Total variance plus : {varplus_total}")
    lines.append(f"Dian : {varplus_dian}")
    lines.append(f"Dinda : {varplus_dinda}")
    lines.append(f"Agung : {varplus_agung}")
    lines.append(f"Rifa : {varplus_rifa}")
    lines.append(f"Putri : {varplus_putri}")
    return "\n".join(lines)

# ===================== Commands =====================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Panduan:\n"
        "• /start → pilih shift\n"
        "• Shift 2: bot minta data Shift 1 dulu (Struk & Variance) → auto isi TRX CPU/Variance Shift 1\n"
        "• Tanggal → sales → struk → (tanya produk khusus) → variance → preview\n"
        "• Tombol /start /help /preview /batal ada di bawah.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_kb()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    kb = [[InlineKeyboardButton("Mulai Laporan KPI", callback_data="start_laporan")]]
    await update.message.reply_text("Selamat datang! Klik tombol untuk mulai laporan.", reply_markup=InlineKeyboardMarkup(kb))

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Sesi di-reset. Ketik /start untuk mulai lagi.", reply_markup=reply_kb())

async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = get_laporan(context)
    if not d.get("shift"):
        await update.message.reply_text("Belum ada data. Ketik /start dulu ya.", reply_markup=reply_kb())
        return
    await update.message.reply_text(render_report(d), parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

# ===================== Inline callbacks =====================
async def on_start_laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data['laporan'] = {}; context.user_data['step'] = None
    kb = [[InlineKeyboardButton("Shift 1", callback_data="shift_1")],
          [InlineKeyboardButton("Shift 2", callback_data="shift_2")]]
    await q.edit_message_text("Pilih shift:", reply_markup=InlineKeyboardMarkup(kb))

async def on_pilih_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    shift = q.data.split("_")[1]
    d = get_laporan(context); d['shift'] = shift

    if shift == '2':
        # Isi dulu data S1 + ceklist dua shift
        ensure_defaults_for_both_shifts(d)
        context.user_data['step'] = 's1_struk_induk_for_s2'
        await q.edit_message_text("Masukkan *Struk Induk Shift 1* (angka, 0 jika tidak ada):", parse_mode=ParseMode.MARKDOWN)
    else:
        ensure_defaults_for_shift(d, '1')
        kb = [[InlineKeyboardButton("Hari ini", callback_data="tgl_today")],
              [InlineKeyboardButton("Input manual", callback_data="tgl_manual")]]
        await q.edit_message_text("Set tanggal:", reply_markup=InlineKeyboardMarkup(kb))

async def on_set_tanggal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    d = get_laporan(context)
    if q.data == "tgl_today":
        d['tanggal'] = datetime.now().strftime("%d/%m/%Y")
        context.user_data['step'] = 'sales_induk'
        await q.edit_message_text("Masukkan *Sales Induk* (angka):", parse_mode=ParseMode.MARKDOWN)
    else:
        context.user_data['step'] = 'tanggal_manual'
        await q.edit_message_text("Ketik tanggal *dd/mm/yyyy* (contoh 22/08/2025):", parse_mode=ParseMode.MARKDOWN)

async def on_produk_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "produk_yes":
        context.user_data['step'] = 'mrbread'
        await q.edit_message_text("Mr Bread berapa? (angka)")
    else:
        context.user_data['step'] = 'variance_induk'
        await q.edit_message_text("Masukkan *Variance Induk* (contoh: +4.139 Dini):", parse_mode=ParseMode.MARKDOWN)

# ===================== Input bertahap =====================
async def input_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    # Map tombol permanen ke command
    if text == "/start":   return await start(update, context)
    if text == "/help":    return await help_cmd(update, context)
    if text == "/preview": return await preview(update, context)
    if text == "/batal":   return await batal(update, context)

    step = context.user_data.get('step')
    d = get_laporan(context)
    if not step:
        await update.message.reply_text("Ketik /start untuk memulai.", reply_markup=reply_kb())
        return

    try:
        # --- SHIFT 2 prefill SHIFT 1 ---
        if step == 's1_struk_induk_for_s2':
            d['s1_struk_induk_for_s2'] = parse_amount(text)
            context.user_data['step'] = 's1_struk_anak_for_s2'
            await update.message.reply_text("Masukkan *Struk Anak Shift 1* (angka, 0 jika tidak ada):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        elif step == 's1_struk_anak_for_s2':
            d['s1_struk_anak_for_s2'] = parse_amount(text)
            d['trx_cpu_shift1_induk'] = d['s1_struk_induk_for_s2']
            d['trx_cpu_shift1_anak']  = d['s1_struk_anak_for_s2']
            context.user_data['step'] = 's1_variance_induk_for_s2'
            await update.message.reply_text("Masukkan *Variance Induk Shift 1* (contoh: +4.139 Dini):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        elif step == 's1_variance_induk_for_s2':
            d['variance_shift1_induk'] = text
            context.user_data['step'] = 's1_variance_anak_for_s2'
            await update.message.reply_text("Masukkan *Variance Anak Shift 1* (contoh: +334 Rifa):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        elif step == 's1_variance_anak_for_s2':
            d['variance_shift1_anak'] = text
            kb = [[InlineKeyboardButton("Hari ini", callback_data="tgl_today")],
                  [InlineKeyboardButton("Input manual", callback_data="tgl_manual")]]
            context.user_data['step'] = None
            await update.message.reply_text("Set tanggal untuk Shift 2:", reply_markup=InlineKeyboardMarkup(kb))

        # --- Tanggal ---
        elif step == 'tanggal_manual':
            if not valid_tanggal(text):
                await update.message.reply_text("Format salah. Contoh benar: 22/08/2025", reply_markup=reply_kb())
                return
            d['tanggal'] = text
            context.user_data['step'] = 'sales_induk'
            await update.message.reply_text("Masukkan *Sales Induk* (angka):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        # --- Sales ---
        elif step == 'sales_induk':
            d['sales_induk'] = parse_amount(text)
            context.user_data['step'] = 'sales_anak'
            await update.message.reply_text("Masukkan *Sales Anak* (angka):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        elif step == 'sales_anak':
            d['sales_anak'] = parse_amount(text)
            d['total_sales'] = d['sales_induk'] + d['sales_anak']
            context.user_data['step'] = 'struk_induk'
            await update.message.reply_text(f"Total Sales sementara: {fmt_id(d['total_sales'])}\nMasukkan *Struk Induk* (angka):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        # --- Struk -> TRX CPU sesuai shift aktif ---
        elif step == 'struk_induk':
            d['struk_induk'] = parse_amount(text)
            context.user_data['step'] = 'struk_anak'
            await update.message.reply_text("Masukkan *Struk Anak* (angka):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        elif step == 'struk_anak':
            d['struk_anak'] = parse_amount(text)
            d['total_struk'] = d['struk_induk'] + d['struk_anak']
            s = d.get('shift', '1')
            if s == '1':
                d['trx_cpu_shift1_induk'] = d['struk_induk']
                d['trx_cpu_shift1_anak']  = d['struk_anak']
                ensure_defaults_for_shift(d, '1')
            else:
                d['trx_cpu_shift2_induk'] = d['struk_induk']
                d['trx_cpu_shift2_anak']  = d['struk_anak']
                ensure_defaults_for_both_shifts(d)

            kb = [[InlineKeyboardButton("Ya", callback_data="produk_yes")],
                  [InlineKeyboardButton("Tidak", callback_data="produk_no")]]
            context.user_data['step'] = None
            await update.message.reply_text("Jual *Produk Khusus* hari ini?", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))

        # --- Produk Khusus (per item) ---
        elif step == 'mrbread':
            d['mrbread'] = parse_amount(text)
            context.user_data['step'] = 'primebread'
            await update.message.reply_text("Prime Bread berapa? (angka)", reply_markup=reply_kb())

        elif step == 'primebread':
            d['primebread'] = parse_amount(text)
            context.user_data['step'] = 'telur'
            await update.message.reply_text("Telur berapa? (angka)", reply_markup=reply_kb())

        elif step == 'telur':
            d['telur'] = parse_amount(text)
            context.user_data['step'] = 'buah_import'
            await update.message.reply_text("Buah Import berapa? (angka)", reply_markup=reply_kb())

        elif step == 'buah_import':
            d['buah_import'] = parse_amount(text)
            context.user_data['step'] = 'buah_lokal'
            await update.message.reply_text("Buah Lokal berapa? (angka)", reply_markup=reply_kb())

        elif step == 'buah_lokal':
            d['buah_lokal'] = parse_amount(text)
            d['all_produk'] = (d.get('mrbread', 0) + d.get('primebread', 0) + d.get('telur', 0) +
                               d.get('buah_import', 0) + d.get('buah_lokal', 0))
            context.user_data['step'] = 'variance_induk'
            await update.message.reply_text("Masukkan *Variance Induk* (contoh: +4.139 Dini):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        # --- Variance (ke shift yang benar) ---
        elif step == 'variance_induk':
            s = d.get('shift', '1')
            d[f'variance_shift{s}_induk'] = text
            context.user_data['step'] = 'variance_anak'
            await update.message.reply_text("Masukkan *Variance Anak* (contoh: +334 Rifa):", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        elif step == 'variance_anak':
            s = d.get('shift', '1')
            d[f'variance_shift{s}_anak'] = text
            context.user_data['step'] = None
            await update.message.reply_text(render_report(d), parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

        else:
            await update.message.reply_text("Langkah tidak dikenali. /batal lalu /start untuk ulang.", reply_markup=reply_kb())
            context.user_data['step'] = None

    except Exception as e:
        await update.message.reply_text(f"Input tidak valid: {e}\nCoba lagi.", parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb())

# ===================== Main =====================
def main():
    import os
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Environment variable BOT_TOKEN belum di-set.")

    base_url = os.environ.get("WEBHOOK_BASE_URL", "").rstrip("/")
    port = int(os.environ.get("PORT", "10000"))

    from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

    app = ApplicationBuilder().token(token).build()

    # === handlers kamu yang sudah ada ===
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("preview", preview))
    app.add_handler(CommandHandler("batal", batal))
    app.add_handler(CallbackQueryHandler(on_start_laporan, pattern="^start_laporan$"))
    app.add_handler(CallbackQueryHandler(on_pilih_shift,   pattern="^shift_[12]$"))
    app.add_handler(CallbackQueryHandler(on_set_tanggal,   pattern="^tgl_(today|manual)$"))
    app.add_handler(CallbackQueryHandler(on_produk_choice, pattern="^produk_(yes|no)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, input_text))

    if base_url:
        # WEBHOOK (untuk Web Service gratis: Render/Koyeb)
        path = token  # secret path
        print(f"Webhook on 0.0.0.0:{port} → {base_url}/{path}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=path,
            webhook_url=f"{base_url}/{path}",
            drop_pending_updates=True,
        )
    else:
        # POLLING (untuk lokal/VPS/worker)
        print("Polling mode (no WEBHOOK_BASE_URL set).")
        app.run_polling()


if __name__ == "__main__":
    main()
