function startVoice(btn, onText, say) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { say(t("ai_unsup")); return; }
  let rec;
  try { rec = new SR(); } catch (e) { say(t("ai_blocked")); return; }
  rec.lang = lang === "de" ? "de-DE" : "en-GB"; rec.interimResults = true; rec.maxAlternatives = 1;
  let finalText = "";
  btn.classList.add("rec"); say(t("ai_listen"));
  rec.onresult = ev => { let txt = ""; for (const res of ev.results) txt += res[0].transcript; finalText = txt; onText(txt, false); };
  rec.onerror = ev => { btn.classList.remove("rec"); say(ev.error === "not-allowed" || ev.error === "service-not-allowed" || ev.error === "audio-capture" ? t("ai_blocked") : t("ai_unsup")); };
  rec.onend = () => { btn.classList.remove("rec"); if (finalText) onText(finalText, true); };
  try { rec.start(); } catch (e) { btn.classList.remove("rec"); say(t("ai_blocked")); }
}
