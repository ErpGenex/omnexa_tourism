# قائمة التحقق UAT — Hotel Front Office (Omnexa Tourism)

**الموقع:** `erpgenex.local.site`  
**المجال:** إدارة الفندق الأمامية + التكامل الخلفي (حجوزات، خدمات، مرافق، POS، فواتير)  
**الهدف:** اعتماد التشغيل وفق سياسة الفروع والصلاحيات.

---

## 1) بيانات الجلسة

- **اسم المختبر:** ____________________
- **الدور:** `Hotel Front Desk` / `Hotel Branch Manager` / `Hotel General Manager`
- **التاريخ:** ____________________
- **الفرع الافتراضي للمستخدم:** ____________________

---

## 2) فحص الوصول والمساحات

### 2.1 مساحة العمل
- [ ] تظهر مساحة `Hotel Front Office` في Desk.
- [ ] تظهر بطاقات KPI وعددها 6.
- [ ] تظهر الرسوم البيانية وعددها 4.
- [ ] تظهر روابط: Booking / Online Request / Guest Folio / Service Order / Restaurant Reservation / Beach Booking / Activity Booking / POS-Billing / Reports.

### 2.2 سياسة الفروع (أهم بند)

#### مستخدم Front Desk / Branch Manager
- [ ] يرى فقط سجلات الفرع المصرح له في `User Branch Access`.
- [ ] لا يمكنه فتح أو تعديل سجل من فرع آخر (رفض صلاحية).
- [ ] عند إنشاء سجل جديد يتم ضبط `branch` تلقائيًا على فرعه.

#### مستخدم General Manager
- [ ] يرى جميع الفروع في القوائم والتقارير.
- [ ] يمكنه التصفية على أي فرع.

---

## 3) سيناريوهات التشغيل الأساسية

### 3.1 دورة الحجز
- [ ] إنشاء `Tourism Booking` بحالة `Confirmed`.
- [ ] الانتقال إلى `Checked In` ينشئ/يربط `Guest Folio` تلقائيًا.
- [ ] الانتقال إلى `Checked Out` ينشئ مهمة `Housekeeping Task` تلقائيًا.
- [ ] لا يسمح بتداخل حجز لنفس الغرفة في نفس الفترة.

### 3.2 الطلبات الأونلاين
- [ ] إنشاء `Tourism Online Booking Request` بحالة `New`.
- [ ] تظهر ضمن تنبيه الإشعارات الخاصة بالطلبات المعلقة.
- [ ] تحويل الطلب إلى عملية تشغيلية (Booking/Reservation/...) يعمل حسب النوع.

### 3.3 الخدمات والمرافق
- [ ] إنشاء `Tourism Service Order` وربطه بحجز/فوليو.
- [ ] عند `Billed` يتم إنشاء `Charge Entry`.
- [ ] اختبار `Restaurant Reservation` مع حالة `Confirmed`.

### 3.4 الفوليو والتحصيل
- [ ] يظهر `balance_due` صحيح في `Tourism Guest Folio`.
- [ ] الفوليو المفتوح المديون يظهر في KPI والتنبيهات.

---

## 4) التقارير الجديدة (Front Office)

- [ ] `Tourism Front Office Arrivals Departures` يعمل مع فلاتر (Company/Branch/Date).
- [ ] `Tourism Service Order Backlog` يعرض المتأخرات بشكل صحيح.
- [ ] `Tourism POS Sales Summary` يعرض التجميع حسب `charge_type` و`branch`.

**تحقق إضافي:**
- [ ] المستخدم الفرعي يرى فقط بيانات فرعه داخل التقرير.
- [ ] المدير العام يرى كل الفروع داخل التقرير.

---

## 5) إشعارات و SLA

### 5.1 إشعارات Desk
- [ ] تظهر عدادات إشعارات لـ:
  - `Tourism Online Booking Request`
  - `Tourism Booking` (وصول/مغادرة + استثناءات)
  - `Tourism Guest Folio`
  - `Tourism Service Order`
  - `Tourism Housekeeping Task`

### 5.2 SLA Hourly/Daily
- [ ] الوظيفة `omnexa_tourism.tasks.hourly` تعمل بدون أخطاء.
- [ ] الوظيفة `omnexa_tourism.tasks.daily` تعمل بدون أخطاء.
- [ ] يتم إنشاء `ToDo` تلقائيًا للحالات:
  - No-show risk
  - Late checkout
  - Housekeeping overdue
  - Service order overdue
  - Web request pending > 2h
  - Outstanding folio aging
- [ ] لا تتكرر نفس الـ ToDo طالما ما زالت `Open`.

---

## 6) معايير قبول دولية (تشغيلية)

- [ ] Traceability: كل طلب/حجز/خدمة له مرجع واضح (Booking/Folio/Reference Doc).
- [ ] Separation of Duties: دور الفرع لا يتجاوز فرعه.
- [ ] Branch Governance: المدير العام فقط يملك رؤية شاملة عبر الفروع.
- [ ] Operational Control: المتأخرات الحرجة لها تنبيه + إجراء (ToDo).
- [ ] Revenue Control: خدمات ومبيعات POS تنعكس في `Charge Entry`/التقارير.

---

## 7) قرار الاعتماد

- [ ] **Pass** — النظام جاهز تشغيل فعلي.
- [ ] **Pass with minor notes** — ملاحظات غير مانعة.
- [ ] **Fail** — يوجد موانع تشغيل.

**ملاحظات الفريق:**

1. ________________________________________________
2. ________________________________________________
3. ________________________________________________

**توقيع مدير الفرع:** ____________________  
**توقيع المدير العام:** ____________________  
**توقيع فريق التقنية:** ____________________
