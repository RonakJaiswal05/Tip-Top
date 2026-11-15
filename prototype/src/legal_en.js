const LEGAL_EN = {
impressum: { nav:"Legal notice", h:"Legal notice", sec:[
  ["Information under § 5 DDG", `<p>TLAMO GmbH<br>trading as “TipTop Service 24”<br>Beusselstraße 18<br>10553 Berlin<br>Germany</p><p>Second shop: Havelstraße 8, 13597 Berlin-Spandau</p>`],
  ["Represented by", `<p>Managing director: ${fillIn("first and last name")}</p>`],
  ["Contact", `<p>Phone: ${LG_TEL}<br>Email: ${LG_MAIL}<br>WhatsApp: +49 176 72746296</p>`],
  ["Company register", `<p>Entered in the commercial register<br>Register court: Amtsgericht Charlottenburg (Berlin)<br>Register number: HRB ${fillIn("number")} B</p>`],
  ["VAT", `<p>VAT identification number under § 27a of the German VAT Act: DE326279747</p>`],
  ["Master workshop", `<p>Entered in the register of crafts of the Handwerkskammer Berlin, Blücherstraße 68, 10961 Berlin.<br>Professional title: ${fillIn("e.g. Informationstechniker-Meister")}, awarded in Germany.<br>Professional rules: German Crafts Code (Handwerksordnung), available at ${extL("https://www.gesetze-im-internet.de/hwo/", "gesetze-im-internet.de/hwo")}.</p><p>${fillIn("Only include if the business is entered in the register of crafts. Otherwise remove this section.")}</p>`],
  ["Responsible for content under § 18 (2) MStV", `<p>${fillIn("first and last name")}<br>Beusselstraße 18, 10553 Berlin</p>`],
  ["Consumer dispute resolution", `<p>We are neither willing nor obliged to take part in dispute resolution proceedings before a consumer arbitration board.</p>`],
  ["Liability for content and links", `<p>We create the content of this website with care. Prices and repair times can change; the price we tell you before the repair is binding. The operators of external websites we link to are responsible for their content. No legal violations were apparent when we added the links. If we become aware of any, we remove the link straight away.</p>`],
  ["Image credits", `<p>Photos: ${fillIn("enter photographer or source")}</p>`],
  ["Design and development", `<p>Ronak</p>`]
]},

datenschutz: { nav:"Privacy", h:"Privacy policy", intro:"This page explains which data we process when you use our website, request a repair or sell us a device, why we need it and what your rights are.", sec:[
  ["Controller", `<p>The controller for data processing on this website and in our shops is:</p><p>TLAMO GmbH (TipTop Service 24)<br>Beusselstraße 18, 10553 Berlin, Germany<br>Phone: ${LG_TEL}<br>Email: ${LG_MAIL}</p><p>Represented by the managing director: ${fillIn("first and last name")}</p>`],
  ["Data protection officer", `<p>${fillIn("If a data protection officer has been appointed: enter name and contact. Otherwise remove this section.")} For any privacy question, write to ${LG_MAIL}.</p>`],
  ["The short version", ulist([
    "You can use the website without an account and without giving us any data.",
    "We only receive data about you when you call, write, submit a form or send a WhatsApp message.",
    "Statistics and marketing services only load if you agree to them in the cookie settings.",
    "The website and database run on servers in Germany. We never sell data."
  ])],
  ["Legal bases", `<p>We process personal data under the General Data Protection Regulation (GDPR) and the German Federal Data Protection Act (BDSG). Depending on the purpose, we rely on:</p>${ulist([
    "Art. 6(1)(a) GDPR: your consent, which you can withdraw at any time for the future,",
    "Art. 6(1)(b) GDPR: performing a contract or pre-contractual steps, such as a repair request,",
    "Art. 6(1)(c) GDPR: legal obligations, such as retention duties under commercial and tax law,",
    "Art. 6(1)(f) GDPR: our legitimate interest, such as running the website securely."
  ])}<p>Storing and reading information on your device is also governed by § 25 of the German Telecommunications Digital Services Data Protection Act (TDDDG).</p>`],
  ["Hosting and server logs", `<p>The website is hosted by Hetzner Online GmbH, Industriestr. 25, 91710 Gunzenhausen, Germany, on servers in Germany. We have a data processing agreement with Hetzner under Art. 28 GDPR.</p><p>Every time a page is requested, the server stores technical data sent by your browser: IP address, date and time, the page requested, the previous page, browser and operating system. We need this to run the website reliably and securely and to fend off attacks (Art. 6(1)(f) GDPR). Logs are deleted after ${fillIn("14")} days unless they are needed to investigate a security incident.</p>`],
  ["Encryption", `<p>The website uses TLS encryption, shown by the padlock and “https://” in the address bar. Data you send us through the website cannot be read by third parties.</p>`],
  ["Cookies, local storage and your consent", `<p>Without your consent we only store what is strictly necessary to run the website on your device, such as your language and your cookie choice (§ 25(2) no. 2 TDDDG). We only use statistics and marketing with your consent (§ 25(1) TDDDG, Art. 6(1)(a) GDPR).</p><p>We manage your choice with our own solution, without an external provider. We store the categories you chose, the version of the notice, the time and a random ID as proof. After 12 months we ask again. You can change or withdraw your choice at any time via “Cookie settings” at the bottom of every page. Every entry is listed in the ${intL("cookies", "cookie policy")}.</p>`],
  ["Price calculator, callback and repair request", `<p>You can use the price calculator without giving any personal data. Only when you request a callback or submit the “Repair request” form do we process what you enter: name, phone or WhatsApp number, device and model, the repair you chose, your description of the problem and how you want to be contacted and repaired.</p><p>We only use this data to answer your request and carry out the repair (Art. 6(1)(b) GDPR). Requests are stored in our admin system on our server in Germany and also copied to a Google Sheets spreadsheet our team works from.</p><p>Requests that do not lead to a repair are deleted after 6 months. For repairs, we keep order and invoice data for as long as commercial and tax law requires, usually 6 to 10 years (Art. 6(1)(c) GDPR).</p>`],
  ["Google Sheets", `<p>We use Google Sheets (Google Workspace) from Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Ireland, to handle requests. We have a data processing agreement with Google under Art. 28 GDPR. A transfer to Google LLC in the USA cannot be ruled out. Google LLC is certified under the EU-US Data Privacy Framework, which is covered by an adequacy decision of the European Commission (Art. 45 GDPR). EU standard contractual clauses also apply.</p>`],
  ["WhatsApp", `<p>The WhatsApp buttons open a chat with us with your repair or device already filled in as a message. Clicking does not send us anything yet. Only when you send the message do we receive your phone number, profile name and the message.</p><p>WhatsApp is operated by WhatsApp Ireland Limited, Merrion Road, Dublin 4, D04 X2K5, Ireland, part of the Meta group. WhatsApp's privacy policy applies, and processing in the USA is possible. We use WhatsApp Business to answer your request (Art. 6(1)(b) GDPR). If you would rather not use WhatsApp, you can reach us just as well by phone, email, form or in a shop. We delete chats no later than ${fillIn("6 months")} after the repair is complete.</p>`],
  ["Phone and email", `<p>When you call or write to us, we process your details to handle your request (Art. 6(1)(b) or (f) GDPR). We delete emails once they are dealt with and no retention duty applies.</p>`],
  ["Voice input", `<p>You can dictate your problem using the microphone button. Voice input only starts after you tap the button, confirm our notice and allow your browser to use the microphone. Your browser's speech recognition (Web Speech API) turns speech into text. Depending on the browser, the recording is sent to its maker for this: Google LLC for Chrome, Microsoft Corporation for Edge, Apple for Safari. We never receive the audio, only the recognised text in the input field.</p><p>The legal basis is your consent (Art. 6(1)(a) GDPR), given when you confirm the notice. Voice input is optional; typing works just as well.</p>`],
  ["Automatic reading of your problem description", `<p>When you describe your problem in your own words, the website picks out the device, model and repair and suggests the matching price. This runs in your browser or on our server in Germany. No data is sent to external AI providers, and there is no automated decision under Art. 22 GDPR: you decide whether to use the suggestion.</p><p>${fillIn("If the live site uses an external AI service: add the provider, purpose and transfer here.")}</p>`],
  ["Selling us a device", `<p>When you sell us a device, we process the details needed for the purchase contract: name, address, date of birth, type and number of your ID, device details including serial number or IMEI, the price and payment details. This is necessary for the contract (Art. 6(1)(b) GDPR) and serves our legitimate interest in preventing the purchase of stolen devices and being able to show who we bought a device from (Art. 6(1)(f) GDPR). For this we check the IMEI against blocklists.</p><p>We keep purchase records for ${fillIn("6 years")}. Any data still on the device is fully erased before resale.</p>`],
  ["Pickup and mail-in", `<p>For the free pickup service we process your address and pickup time; for mail-in repairs, your address for the return. We pass name and address to the delivery company ${fillIn("e.g. DHL Paket GmbH")} where needed for delivery (Art. 6(1)(b) GDPR).</p>`],
  ["Your data on the device during repair", `<p>We only access the contents of your device where strictly necessary for the repair and function test. We do not copy anything and do not look at photos, messages or files. We only carry out data recovery on your instruction; we hand the recovered data to you and then delete our working copy.</p>`],
  ["Fonts", `<p>The Archivo typeface is stored on our own server. No connection to Google Fonts or any other font provider is made when you open the site.</p>`],
  ["Links to Google Maps and Instagram", `<p>The “Directions” buttons and the Instagram link are plain links. Only when you click them do you go to Google Maps (Google Ireland Limited) or Instagram (Meta Platforms Ireland Limited, Merrion Road, Dublin 4, Ireland), whose privacy policies then apply. No data is sent to these providers before that.</p>`],
  ["Statistics with Matomo (consent only)", `<p>If you agree to “Statistics”, we use Matomo, open-source analytics software that we run on our own server in Germany. Matomo sets cookies and records pages viewed, time on page, device type and where the visit came from. Your IP address is shortened by two bytes before storage, so we cannot identify you. The data never leaves our server and is deleted after ${fillIn("13")} months.</p><p>The legal basis is your consent (§ 25(1) TDDDG, Art. 6(1)(a) GDPR). If you withdraw it in the cookie settings, we delete the Matomo cookies on your device.</p>`],
  ["Marketing (consent only)", `<p>If you agree to “Marketing”, we load Google Ads conversion tracking (Google Ireland Limited) and the Meta Pixel (Meta Platforms Ireland Limited). This tells us whether an ad led to a request and lets us target ads in Berlin more precisely. Cookies are set and usage data such as IP address, device information and interactions are sent to Google or Meta, including to the USA. Both companies are certified under the EU-US Data Privacy Framework. We are jointly responsible with Meta for data collected through the Meta Pixel (Art. 26 GDPR).</p><p>The legal basis is your consent (§ 25(1) TDDDG, Art. 6(1)(a) GDPR), which you can withdraw at any time. ${fillIn("Only include if ads are run. Otherwise remove this section and the category.")}</p>`],
  ["Admin area", `<p>The admin area is only accessible to our team. Signing in uses strictly necessary cookies for the session and to protect against cross-site attacks. Changes to prices and requests are logged so we can see who changed what.</p>`],
  ["How long we keep data", `<p>We only keep personal data for as long as needed for the purpose or required by law. The periods for each type of processing are listed above. After that we delete the data, or restrict it where a retention duty applies.</p>`],
  ["Your rights", `<p>You have the right at any time to</p>${ulist([
    "access the data we hold about you (Art. 15 GDPR),",
    "have incorrect data corrected (Art. 16 GDPR),",
    "have data erased (Art. 17 GDPR),",
    "restrict processing (Art. 18 GDPR),",
    "data portability (Art. 20 GDPR),",
    "withdraw consent for the future (Art. 7(3) GDPR)."
  ])}<p>A short message to ${LG_MAIL} or a visit to a shop is enough.</p>`],
  ["Right to object", `<p><strong>Where we process data based on our legitimate interest (Art. 6(1)(f) GDPR), you can object at any time on grounds relating to your particular situation (Art. 21(1) GDPR). We will then stop, unless we can show compelling legitimate grounds that override your interests or the processing is needed to establish, exercise or defend legal claims. You can object to processing for advertising at any time without giving reasons (Art. 21(2) GDPR).</strong></p>`],
  ["Right to complain", `<p>You can complain to a data protection supervisory authority (Art. 77 GDPR). Ours is:</p><p>Berliner Beauftragte für Datenschutz und Informationsfreiheit<br>Alt-Moabit 59–61, 10555 Berlin<br>Phone +49 30 13889-0<br>${extL("https://www.datenschutz-berlin.de")}</p>`],
  ["Providing data and automated decisions", `<p>You are not legally or contractually required to give us any data. Without a name and phone number we cannot call you back, though, and without ID details we cannot buy a device from you. There is no automated decision-making or profiling under Art. 22 GDPR.</p>`],
  ["Changes", `<p>We update this policy when the website, our processes or the law change. The version published here applies.</p>`]
]},

agb: { nav:"Terms", h:"Terms and conditions", intro:"For repairs and for selling devices to TipTop Service 24.", sec:[
  ["@Part A: Repairs"],
  ["§ 1 Scope", abs([
    "These terms apply to all repair, diagnosis and purchase contracts between TLAMO GmbH, trading as “TipTop Service 24”, Beusselstraße 18, 10553 Berlin (“TipTop”), and its customers (“customer”), whether the contract is made in a shop, by phone, via WhatsApp or through the website.",
    "Conflicting terms of the customer only apply if TipTop expressly agrees to them in text form.",
    "A consumer is any natural person who enters into a transaction for purposes that are mainly outside their trade, business or profession (§ 13 BGB)."
  ])],
  ["§ 2 Website prices and contract", abs([
    "Prices in the price calculator are final prices including 19% VAT for the stated repair on the stated model. Showing them on the website is not yet a binding offer. Prices marked “from” are minimum prices; the exact price is set after diagnosis.",
    "The repair contract is made when the customer hands in the device at a shop and confirms the repair order, or when TipTop confirms an order for pickup or mail-in placed by phone, WhatsApp or through the website. Callback and request forms are non-binding enquiries.",
    "If the diagnosis reveals further damage that would raise the agreed price, TipTop asks the customer before doing any extra work."
  ])],
  ["§ 3 Diagnosis and estimates", abs([
    `Diagnosis is free if the customer then orders the repair. If the customer declines the repair after diagnosis, TipTop charges ${fillIn("a flat fee of … €")}, provided this was agreed before the diagnosis.`,
    "An estimate is non-binding unless expressly marked as binding. If it looks like it will be exceeded significantly, TipTop tells the customer before continuing (§ 649 BGB)."
  ])],
  ["§ 4 Parts: Original and Premium", abs([
    "“Original” means parts made by the device manufacturer or supplied by the manufacturer for repair.",
    "“Premium” means high-quality compatible parts from other makers that TipTop tests for function, brightness, colour and touch before fitting. Displays may differ slightly from the original in brightness, colour and power use. Some manufacturers show a notice in the settings after a third-party part is fitted, such as “Unknown part” on iPhones; this does not limit function.",
    "The customer chooses the part quality before the repair. Removed parts are returned on request; otherwise TipTop disposes of them properly."
  ])],
  ["§ 5 Customer duties before the repair", abs([
    "The customer backs up all data on the device before handing it in. Even with careful work, data can be lost during a repair. TipTop is only liable for data loss under § 12.",
    "The customer removes SIM and memory cards, cases and accessories.",
    "Where needed for the function test, the customer gives the unlock code or is present at handover to test. This is optional; without a code TipTop can only test in part."
  ])],
  ["§ 6 Repair time", `<p>Stated repair times, such as “under an hour”, are guidelines. If a part has to be ordered, TipTop gives the expected time. Only expressly promised dates are binding.</p>`],
  ["§ 7 Pickup and mail-in", abs([
    "Within 5 km of a shop, TipTop collects the device free of charge at an agreed time and brings it back repaired.",
    "For mail-in repairs the customer packs the device safely and without accessories. Return shipping is free for the customer. For consumers, TipTop bears the risk during return shipping until handover.",
    `Consumers have a right of withdrawal for contracts made exclusively by distance communication. Details are in the ${intL("widerruf", "withdrawal policy")}.`
  ])],
  ["§ 8 Payment, collection and uncollected devices", abs([
    `The repair price is due when the device is returned. Payment by cash or card ${fillIn("or bank transfer")}.`,
    "TipTop has a statutory lien on the device for its claims under the repair contract (§ 647 BGB).",
    `If the customer does not collect the repaired device within 4 weeks of being told it is ready, TipTop sends a reminder with a reasonable deadline. After that, TipTop may charge reasonable storage fees or proceed as permitted by law. ${fillIn("Check period and storage fee.")}`
  ])],
  ["§ 9 Statutory warranty", `<p>Statutory rights for defects apply to repair work and fitted parts. The limitation period is two years from acceptance (§ 634a BGB). Customers can report defects in a shop, by phone or by email.</p>`],
  ["§ 10 Guarantee", abs([
    "In addition to the statutory rights, TipTop gives a voluntary guarantee on fitted parts and the work done. Depending on the repair and part quality it lasts up to 24 months; the exact period is on the invoice.",
    "The guarantor is TLAMO GmbH, Beusselstraße 18, 10553 Berlin. The guarantee applies in Germany. In a guarantee case, TipTop checks the device and repairs it free of charge or replaces the affected part. The customer brings the device and invoice to a shop or sends it in.",
    "Excluded is damage from drops, pressure, breakage (especially broken glass), liquids, improper handling and third-party work after the repair.",
    "The customer's statutory rights, in particular those under § 9, are not affected or limited by the guarantee. Using the statutory rights is free of charge."
  ])],
  ["§ 11 Water damage, board repair and data recovery", `<p>For water damage, board-level repairs (micro-soldering, chip replacement) and data recovery, TipTop cannot guarantee success because the condition often only shows during the work. If the repair fails, TipTop only charges the diagnosis or effort price agreed beforehand. Devices already damaged by corrosion can develop further faults even after a successful repair; the guarantee under § 10 does not cover this. Statutory rights for defects are not affected.</p>`],
  ["§ 12 Liability", abs([
    "TipTop is liable without limit for intent and gross negligence, for injury to life, body or health and under the Product Liability Act.",
    "For simple negligence, TipTop is only liable for breach of an essential contractual duty, meaning a duty that makes proper performance of the contract possible in the first place and that the customer may regularly rely on. Liability is then limited to the foreseeable damage typical for the contract.",
    "For loss of data caused by simple negligence, TipTop is only liable for the effort that would have been needed to restore the data had the customer backed it up properly."
  ])],
  ["@Part B: Selling devices to TipTop"],
  ["§ 13 Offer and contract", abs([
    "The offer the customer receives via WhatsApp or the website is a non-binding estimate based on their details and is valid for 7 days.",
    "TipTop sets the binding price after checking the device in a shop. The purchase contract is made when it is signed in the shop, on paper or digitally on a tablet."
  ])],
  ["§ 14 Requirements", abs([
    "The seller must be at least 18 and show valid official photo ID.",
    "The seller confirms that they own the device and may dispose of it freely, that it is not stolen, embezzled, financed, leased or subject to third-party rights, and that their description of its condition is accurate.",
    "Activation locks such as Apple's Find My or the Google account lock must be removed before the sale. TipTop checks the IMEI or serial number against blocklists."
  ])],
  ["§ 15 Data on the device", `<p>The seller backs up and deletes their data before the sale and resets the device to factory settings. TipTop erases any remaining data with a certified process before resale and is not obliged to back up or hand over data.</p>`],
  ["§ 16 Price and payment", `<p>The price is paid immediately when the contract is made, in cash or by transfer to an account in the seller's name.</p>`],
  ["§ 17 False information and blocked devices", `<p>If the seller's confirmations under § 14 turn out to be untrue, in particular if the device is stolen or blocked, TipTop may withdraw from the contract and reclaim the price. Statutory claims remain unaffected. If a crime is suspected, TipTop may hand the device to the police.</p>`],
  ["@Part C: Final provisions"],
  ["§ 18 Consumer dispute resolution", `<p>TipTop is neither willing nor obliged to take part in dispute resolution proceedings before a consumer arbitration board.</p>`],
  ["§ 19 Governing law and jurisdiction", abs([
    "German law applies, excluding the UN Convention on Contracts for the International Sale of Goods. For consumers, this choice of law only applies insofar as it does not remove the protection of mandatory rules of the country where they normally live.",
    "If the customer is a merchant, a legal entity under public law or a special fund under public law, the place of jurisdiction is Berlin."
  ])],
  ["§ 20 Invalid provisions", `<p>If individual provisions are invalid, the rest of the contract remains valid. The statutory provisions take the place of the invalid provision (§ 306 BGB).</p>`]
]},

widerruf: { nav:"Withdrawal", h:"Withdrawal policy", intro:"Applies to repair orders you place entirely at a distance, such as booking pickup or mail-in through the website, by phone or via WhatsApp.", sec:[
  ["Right of withdrawal", `<p>You have the right to withdraw from this contract within fourteen days without giving any reason.</p><p>The withdrawal period is fourteen days from the day the contract is concluded.</p><p>To exercise your right of withdrawal, you must inform us (TLAMO GmbH, TipTop Service 24, Beusselstraße 18, 10553 Berlin, phone +49 30 81475791, email info@tiptophandyreparatur.de) of your decision to withdraw from this contract by a clear statement (e.g. a letter sent by post or an email). You may use the attached model withdrawal form, but this is not obligatory. You can also withdraw using the “Withdraw from contract” function on this page.</p><p>To meet the withdrawal deadline, it is sufficient for you to send your notice of withdrawal before the withdrawal period has expired.</p>`],
  ["Effects of withdrawal", `<p>If you withdraw from this contract, we shall reimburse all payments received from you, including the costs of delivery (with the exception of the supplementary costs resulting from your choice of a type of delivery other than the least expensive type of standard delivery offered by us), without undue delay and in any event not later than fourteen days from the day on which we are informed about your decision to withdraw from this contract. We will carry out such reimbursement using the same means of payment as you used for the initial transaction, unless you have expressly agreed otherwise; in any event, you will not incur any fees as a result of such reimbursement.</p><p>If you requested to begin the performance of services during the withdrawal period, you shall pay us an amount which is in proportion to what has been provided until you have communicated to us your withdrawal from this contract, in comparison with the full coverage of the contract.</p>`],
  ["When the right applies", ulist([
    "Consumers have this right for contracts made exclusively by distance communication, for example when you book pickup or mail-in through the website, by phone, email or WhatsApp.",
    "There is no statutory right of withdrawal for orders you place in one of our shops.",
    "The right expires once we have fully carried out the repair, if you expressly agreed beforehand that we may start before the withdrawal period ends and confirmed that you lose the right once the contract is fully performed (§ 356(4) BGB)."
  ])],
  ["Model withdrawal form", `<div class="lg-form"><p>(Complete and return this form only if you wish to withdraw from the contract.)</p><p>To TLAMO GmbH, TipTop Service 24, Beusselstraße 18, 10553 Berlin, Germany, email: info@tiptophandyreparatur.de:</p><p>I/We (*) hereby give notice that I/We (*) withdraw from my/our (*) contract of sale of the following goods (*)/for the provision of the following service (*)</p><p>Ordered on (*)/received on (*)</p><p>Name of consumer(s)</p><p>Address of consumer(s)</p><p>Signature of consumer(s) (only if this form is notified on paper)</p><p>Date</p><p>(*) Delete as appropriate.</p></div>`]
]},

cookies: { nav:"Cookies", h:"Cookie policy", intro:"Which cookies and storage entries this website uses, what for and for how long.", sec:[
  ["Cookies and local storage", `<p>Cookies and local storage entries are small pieces of data your browser keeps for a website. We use them sparingly: without your consent we only set what is strictly necessary to run the site. Third-party advertising and analytics cookies never load before you agree.</p>`],
  ["Necessary", `<p>We need these for the site to work and remember your choices. The legal basis is § 25(2) no. 2 TDDDG; no consent is required.</p>${ckTable("en", "necessary")}`],
  ["Statistics", `<p>Only with your consent. Helps us see which pages and repairs people look for, so we can improve the site.</p>${ckTable("en", "stats")}`],
  ["Marketing", `<p>Only with your consent. Measures whether our ads lead to requests. ${fillIn("Remove this category if no ads are run.")}</p>${ckTable("en", "marketing")}`],
  ["Legal basis and withdrawal", `<p>We set optional cookies based on your consent (§ 25(1) TDDDG, Art. 6(1)(a) GDPR). You can withdraw it at any time via “Cookie settings” at the bottom of every page. Rejecting is as easy as accepting and has no downside: the price calculator, forms and WhatsApp always work. If you withdraw consent, we delete the related cookies on your device. More in the ${intL("datenschutz", "privacy policy")}.</p>`],
  ["Deleting cookies in your browser", `<p>You can also delete or block cookies and site data yourself in your browser, usually under “Settings”, “Privacy” or “Site data”. We will then ask for your choice again on your next visit.</p>`]
]},

barrierefreiheit: { nav:"Accessibility", h:"Accessibility", intro:"We want everyone to be able to get their device repaired with us, online too.", sec:[
  ["Our service", `<p>On this website you can calculate repair prices, request a repair, ask for a callback, book a pickup via WhatsApp and offer us a device to buy. Everything is also available by phone and in our shops.</p>`],
  ["Standard", `<p>We follow the Web Content Accessibility Guidelines (WCAG) 2.1 at level AA and the harmonised standard EN 301 549.</p>`],
  ["What we do", ulist([
    "Every function works with a keyboard, and the focus is always clearly visible.",
    "Text and controls have enough colour contrast, and information never depends on colour alone.",
    "Buttons, form fields and images have labels and alternative text for screen readers; error messages are announced.",
    "The page can be zoomed to 200% and works on every screen size without sideways scrolling.",
    "If “Reduce motion” is turned on in your system, we switch animations off.",
    "The site is available in German and English, and the language is marked up for screen readers.",
    "You can type, tap or dictate to get a price."
  ])],
  ["Known limitations", ulist([
    "The before and after comparison is a slider. With a keyboard, use the arrow keys; the images are also described in text.",
    "WhatsApp, Google Maps and Instagram are external services whose accessibility we cannot control. Phone, email and the form are available instead.",
    `${fillIn("Add the result of the final audit before launch.")}`
  ])],
  ["Report a barrier", `<p>If you come across a barrier or need help, email ${LG_MAIL} or call ${LG_TEL}. We reply within ${fillIn("14")} days and help you another way in the meantime.</p>`],
  ["Market surveillance authority", `<p>Marktüberwachungsstelle der Länder für die Barrierefreiheit von Produkten und Dienstleistungen (MLBF AöR)<br>Carl-Miller-Straße 6, 39112 Magdeburg, Germany<br>${extL("https://www.mlbf-barrierefrei.de")}</p>`],
  ["Status of this statement", `<p>Self-assessment of 14 November 2026. ${fillIn("Check whether TipTop is exempt from the Accessibility Strengthening Act as a micro-enterprise (fewer than 10 employees and annual turnover of at most €2 million). The statement can then stay voluntary.")}</p>`]
]}
};
