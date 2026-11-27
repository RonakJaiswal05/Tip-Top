# 27 Nov 2026: requests from the Claude Code port (see CLAUDE.md, "Requests for the chat").
# 1. The hours list had overridden T.closed ("geschlossen"), which openStatus() needs for "Geschlossen, öffnet {d} um 10 Uhr".
#    The list now uses its own key closed_day.
rep('closed:"closed", ask_l', 'closed_day:"closed", ask_l')
rep('closed:"geschlossen", ask_l', 'closed_day:"geschlossen", ask_l')
rep('<b>${esc(t("closed"))', '<b>${esc(t("closed_day"))')
# 2. Shop card at 320-380 px and footer hours on phones: same CSS as the Django site (app/static/site/css/port-additions.css).
s = s.replace('</style>', '''/* shop card at 320-380 px: pin the column to the card width, tighten the hours box */
.shop .shop-b{grid-template-columns:minmax(0,1fr)}
@media (max-width:380px){
  .shop .shop-b{padding-left:18px;padding-right:18px}
  .shop .shop-b .srate{flex-wrap:wrap;row-gap:2px}
  .shop .shop-h{padding-left:12px;padding-right:12px;gap:8px}
  .shop .shop-h > .ico{display:none}
  .shop .hours{font-size:14px}
  .shop .hours li{gap:10px}
}
/* footer hours on phones: the time goes under the day if needed */
.fgrid .hours li{flex-wrap:wrap;column-gap:10px;row-gap:0}
@media (max-width:600px){.fgrid .hours{row-gap:10px}}
</style>''', 1)
