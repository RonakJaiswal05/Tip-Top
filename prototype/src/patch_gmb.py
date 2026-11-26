# Google ratings, brand logo slots, trademark note, business WhatsApp number, per-shop phone.
# 25 Nov 2026: the owner wants the shop landline 030 814 757 91 as the WhatsApp number everywhere, so WA_NUMBER stays "493081475791".
rep('// TODO before launch: confirm the shop\'s WhatsApp Business number. Currently the Moabit landline.\n', '// WhatsApp Business number of the shop = the shop landline 030 814 757 91 (owner, 25 Nov 2026)\n')
rep('''  { id:"shop-moabit", area:"Berlin-Moabit", street:"Beusselstraße 18", zip:"10553 Berlin", q:"TipTop Service 24, Beusselstraße 18, 10553 Berlin" },
  { id:"shop-spandau", area:"Berlin-Spandau", street:"Havelstraße 8", zip:"13597 Berlin", q:"Havelstraße 8, 13597 Berlin" }''',
'''  { id:"shop-moabit", g:"moabit", area:"Berlin-Moabit", street:"Beusselstraße 18", zip:"10553 Berlin", q:"TipTop Service 24, Beusselstraße 18, 10553 Berlin", tel:"+493081475791", telTxt:"030 814 757 91" },
  { id:"shop-spandau", g:"spandau", area:"Berlin-Spandau", street:"Havelstraße 8", zip:"13597 Berlin", q:"Havelstraße 8, 13597 Berlin", tel:"+493089617138", telTxt:"030 896 171 38" }''')
rep('<p class="hero-p" data-t="hero_p"></p>', '<p class="hero-p" data-t="hero_p"></p>\n        <div class="gmb-wrap" id="gmbHero"></div>')
rep('<div class="cab" id="brandWall"></div>', '<div class="cab" id="brandWall"></div>\n      <p class="tm-note" data-t="br_tm"></p>')
rep('''  $("askMic").innerHTML = ic("mic");
  watch($("heroMedia"));''', '''  $("askMic").innerHTML = ic("mic");
  $("gmbHero").innerHTML = gmbBadge();
  watch($("heroMedia"));''')
rep('</style>', open('gmb4.css').read() + '\n</style>')
rep('/* ===== Language, routing, boot ===== */', open('gmb4.js').read() + '\n/* ===== Language, routing, boot ===== */')
