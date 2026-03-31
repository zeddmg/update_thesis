// =============================================================================
// createDjezzyForm.gs
// =============================================================================
// Author     : Meguelati Ali Zine El Abidine
// Institution: Batna 1 University – Hadj Lakhdar
// Year       : 2025 – 2026
// Topic      : The Impact Search Engine Optimization (SEO) on Brand Positioning : Using an Automated Analytical Pipeline========
// Description:
//   Creates the complete bilingual survey form programmatically via
//   Google Apps Script (FormApp API), configures all 16 questions across
//   4 sections, and links the form to a new Google Sheets spreadsheet.
//   Every response is automatically written as a timestamped row in Sheets.
//
// Usage:
//   1. Open Google Drive → New → Google Apps Script
//   2. Paste this script
//   3. Run createForm()  (run once – re-running creates a duplicate)
//   4. Check Logs (View → Logs) for the form URL and Sheet URL
//
// NOTE: Run this script exactly ONCE during data collection setup.
// =============================================================================

function createForm() {

  // ── FORM METADATA ──────────────────────────────────────────────────────────
  var FORM_TITLE  = 'The Impact of SEO on Brand Positioning - Djezzy Algeria';
  var SHEET_NAME  = 'Djezzy SEO Survey - Responses';
  var FORM_DESCRIPTION =
    'Dear participant,\n\n' +
    'This questionnaire is part of a 3rd year licence dissertation in Management ' +
    'at Batna 1 University - Hadj Lakhdar. The research examines whether SEO ' +
    '(search engine optimization) affects how Algerian internet users perceive ' +
    'and trust brands — with Djezzy Algeria as the case study.\n\n' +
    'Your answers are anonymous and used only for academic purposes. ' +
    'There is no right or wrong answer — just your honest opinion. ' +
    'Should take about 5 minutes.\n\nThank you for your time.';

  // ── CREATE FORM ─────────────────────────────────────────────────────────────
  var form = FormApp.create(FORM_TITLE);
  form.setDescription(FORM_DESCRIPTION);
  form.setCollectEmail(false);          // anonymous — no email collected
  form.setAllowResponseEdits(false);
  form.setLimitOneResponsePerUser(false);
  form.setProgressBar(true);
  form.setConfirmationMessage(
    'Thank you for participating! Your response has been recorded.\n' +
    'شكراً لمشاركتك! تم تسجيل إجابتك.'
  );

  // ── SECTION A: Personal Information ────────────────────────────────────────
  form.addSectionHeaderItem()
    .setTitle('Section A — Personal Information')
    .setHelpText('أ — المعلومات الشخصية');

  form.addMultipleChoiceItem()
    .setTitle('1. What is your gender?  /  ما هو جنسك؟')
    .setChoiceValues(['Male / ذكر', 'Female / أنثى', 'Prefer not to say / أفضل عدم الإجابة'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('2. What is your age group?  /  ما هي فئتك العمرية؟')
    .setChoiceValues(['18-24', '25-34', '35-44', '45-54', '55+'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('3. What is your highest level of education?  /  ما هو أعلى مستوى تعليمي لديك؟')
    .setChoiceValues([
      'Secondary / High School  /  ثانوي',
      'Undergraduate (Licence)  /  ليسانس',
      'Postgraduate (Master / PhD)  /  ماستر / دكتوراه',
      'Other  /  أخرى'
    ])
    .setRequired(true);

  // ── SECTION B: Internet and Search Engine Usage ─────────────────────────────
  form.addSectionHeaderItem()
    .setTitle('Section B — Internet and Search Engine Usage')
    .setHelpText('ب — استخدام الإنترنت ومحركات البحث');

  form.addMultipleChoiceItem()
    .setTitle('4. How often do you use search engines?  /  كم مرة تستخدم محركات البحث؟')
    .setChoiceValues([
      'Multiple times a day  /  عدة مرات يومياً',
      'Once a day  /  مرة واحدة يومياً',
      'A few times per week  /  عدة مرات في الأسبوع',
      'Rarely  /  نادراً',
      'Never  /  لا أستخدمها'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('5. Which search engine do you use most?  /  أي محرك بحث تستخدم أكثر؟')
    .setChoiceValues(['Google', 'Bing', 'Yahoo', 'Other  /  أخرى'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle(
      '6. When you want to learn about a new product or service, what do you do first?\n' +
      'عندما تريد معرفة المزيد عن منتج أو خدمة جديدة، ماذا تفعل أولاً؟'
    )
    .setChoiceValues([
      'Search on Google  /  أبحث على Google',
      'Ask friends / family  /  أسأل الأصدقاء أو العائلة',
      'Check social media  /  أتصفح وسائل التواصل الاجتماعي',
      'Visit the company website directly  /  أزور موقع الشركة مباشرة'
    ])
    .setRequired(true);

  // ── SECTION C: Djezzy Algeria and Digital Discovery ─────────────────────────
  form.addSectionHeaderItem()
    .setTitle('Section C — Djezzy Algeria and Digital Discovery')
    .setHelpText('ج — جازي الجزائر والاكتشاف الرقمي');

  form.addMultipleChoiceItem()
    .setTitle(
      '7. Have you ever searched for Djezzy Algeria on a search engine?\n' +
      'هل سبق لك البحث عن جازي الجزائر على محرك بحث؟'
    )
    .setChoiceValues(["Yes  /  نعم", "No  /  لا", "I'm not sure  /  لست متأكداً"])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle(
      '8. How did you first hear about Djezzy Algeria?\n' +
      'كيف عرفت عن جازي الجزائر لأول مرة؟'
    )
    .setChoiceValues([
      'Google or other search engine  /  Google أو محرك بحث آخر',
      'Social media (Facebook, Instagram, etc.)  /  وسائل التواصل الاجتماعي',
      'Recommendation from a friend or family member  /  توصية من صديق أو فرد من العائلة',
      'Television or radio advertising  /  إعلان تلفزيوني أو إذاعي',
      'Billboard or outdoor advertising  /  لافتة إعلانية',
      'Other  /  أخرى'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle(
      '9. When you search for Djezzy Algeria on Google, which page does the company appear on?\n' +
      'عندما تبحث عن جازي الجزائر على Google، في أي صفحة تظهر الشركة؟'
    )
    .setChoiceValues([
      'Page 1 (positions 1-10)  /  الصفحة الأولى (المراكز 1-10)',
      'Page 2  /  الصفحة الثانية',
      'Page 3 or beyond  /  الصفحة الثالثة أو أبعد',
      'I have never searched for this  /  لم أبحث عن هذا من قبل'
    ])
    .setRequired(true);

  // ── SECTION D: SEO and Brand Perception — Likert Scale (1–5) ───────────────
  form.addSectionHeaderItem()
    .setTitle('Section D — Attitudes Toward SEO and Brand Perception')
    .setHelpText(
      'د — المواقف تجاه تحسين محركات البحث وإدراك العلامة التجارية\n' +
      'Rate your agreement: 1 = Strongly Disagree … 5 = Strongly Agree\n' +
      'قيّم موافقتك: 1 = أعارض بشدة … 5 = أوافق بشدة'
    );

  var statements = [
    'Q1: A brand that appears at the top of Google results has a better image in my mind.\n' +
    'علامة تجارية تظهر في أعلى نتائج Google تحتل صورة أفضل في ذهني.',

    'Q2: If I cannot find a brand on Google, I consider it less serious and less reliable.\n' +
    'إذا لم أجد علامة تجارية على Google، أعتبرها أقل جدية وموثوقية.',

    'Q3: The ranking position of a company on Google influences my decision to contact or buy.\n' +
    'موضع ترتيب الشركة على Google يؤثر في قراري بالتواصل معها أو الشراء منها.',

    'Q4: I trust Djezzy Algeria more because I can easily find its website on Google.\n' +
    'أثق في جازي الجزائر أكثر لأنني أجد موقعها بسهولة على Google.',

    'Q5: A company\'s visibility on search engines reflects the quality of its services.\n' +
    'ظهور الشركة على محركات البحث يعكس جودة خدماتها.',

    'Q6: I would choose an operator that ranks #1 on Google over one that does not appear.\n' +
    'أختار مشغلاً يحتل المركز الأول على Google على حساب مشغل لا يظهر.',

    'Q7: I believe Djezzy Algeria is investing enough in its online visibility.\n' +
    'أعتقد أن جازي الجزائر تستثمر بما يكفي في ظهورها على الإنترنت.'
  ];

  for (var i = 0; i < statements.length; i++) {
    form.addScaleItem()
      .setTitle(statements[i])
      .setBounds(1, 5)
      .setLabels('1 — Strongly Disagree  /  أعارض بشدة',
                 '5 — Strongly Agree  /  أوافق بشدة')
      .setRequired(true);
  }

  // ── LINK TO GOOGLE SHEETS ───────────────────────────────────────────────────
  // Creates a new Sheets spreadsheet and links the form to it.
  // Google Forms will automatically write every new response as a new row,
  // including a server-generated timestamp.
  var ss = SpreadsheetApp.create(SHEET_NAME);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // ── LOG URLS ────────────────────────────────────────────────────────────────
  Logger.log('========================================');
  Logger.log('Form created successfully!');
  Logger.log('Edit URL  : ' + form.getEditUrl());
  Logger.log('Share URL : ' + form.getPublishedUrl());
  Logger.log('Sheet URL : ' + ss.getUrl());
  Logger.log('Sheet ID  : ' + ss.getId());
  Logger.log('Form ID   : ' + form.getId());
  Logger.log('========================================');
  Logger.log('Next step: copy the Sheet ID into sheets_reader.py');
}
