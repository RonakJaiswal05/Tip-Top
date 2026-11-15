"""Line icons from the prototype (24×24, stroke = currentColor)."""
from django.utils.safestring import mark_safe

IC = {
    'display': '<rect x="6" y="2.5" width="12" height="19" rx="2.4"/><path d="M9.5 7l2.5 3.5-2 2.5 3.5 3.5"/>',
    'battery': '<rect x="2.5" y="7.5" width="17" height="9" rx="1.8"/><path d="M21.5 10.5v3M6 10.5v3M9.5 10.5v3"/>',
    'port': '<path d="M9 3v5M15 3v5M7 8h10v3.5a5 5 0 0 1-10 0z"/><path d="M12 16.5V21"/>',
    'back': '<rect x="6" y="2.5" width="12" height="19" rx="2.4"/><rect x="8.3" y="5" width="4.4" height="4.4" rx="1.2"/>',
    'camera': '<path d="M4 7.5h3l2-2.5h6l2 2.5h3v11H4z"/><circle cx="12" cy="13" r="3.2"/>',
    'camglass': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.5"/><path d="M8 6.5l2 2.5"/>',
    'frontcam': '<rect x="6" y="2.5" width="12" height="19" rx="2.4"/><circle cx="12" cy="5.6" r="1"/>',
    'faceid': '<path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5a1.5 1.5 0 0 1-1.5 1.5H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16M9 9.5v1M15 9.5v1M12 9.5v3.5h-1M9 15.5c2 1.5 4 1.5 6 0"/>',
    'speaker': '<path d="M4 9h3.5L13 5v14l-5.5-4H4z"/><path d="M16.5 9a4 4 0 0 1 0 6M19 6.5a7.5 7.5 0 0 1 0 11"/>',
    'earpiece': '<path d="M8 15c0 2.5 1.6 4 3.5 4S15 17.6 15 15.5c0-2.6 3-3.3 3-7.5a6 6 0 0 0-12 0"/>',
    'mic': '<path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3z"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    'water': '<path d="M12 3s6 6.8 6 11a6 6 0 0 1-12 0c0-4.2 6-11 6-11z"/>',
    'mainboard': '<rect x="7" y="7" width="10" height="10" rx="1.2"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    'data': '<ellipse cx="12" cy="6" rx="7.5" ry="2.8"/><path d="M4.5 6v12c0 1.6 3.4 2.8 7.5 2.8s7.5-1.2 7.5-2.8V6M4.5 12c0 1.6 3.4 2.8 7.5 2.8s7.5-1.2 7.5-2.8"/>',
    'diagnosis': '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
    'software': '<path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13.5 5.5l-3 13"/>',
    'buttons': '<path d="M12 3v7.5"/><path d="M7.2 6.3a7.5 7.5 0 1 0 9.6 0"/>',
    'vibration': '<rect x="8" y="4.5" width="8" height="15" rx="1.8"/><path d="M4.5 9v6M19.5 9v6"/>',
    'sim': '<path d="M7 3h7l4 4v14H7z"/><rect x="9.5" y="11.5" width="6" height="6" rx="1"/>',
    'jack': '<path d="M4 15.5V12a8 8 0 0 1 16 0v3.5"/><rect x="3" y="14.5" width="4" height="6" rx="1.2"/><rect x="17" y="14.5" width="4" height="6" rx="1.2"/>',
    'keyboard': '<rect x="2.5" y="6.5" width="19" height="11" rx="1.8"/><path d="M6 10h.01M9 10h.01M12 10h.01M15 10h.01M18 10h.01M7.5 14h9"/>',
    'trackpad': '<rect x="4" y="4" width="16" height="16" rx="2.5"/><path d="M4 15h16M12 15v5"/>',
    'hinge': '<path d="M5 4h14v10H5z"/><path d="M3 17h18"/>',
    'fan': '<circle cx="12" cy="12" r="1.8"/><path d="M12 10.2c0-4 2.5-6.2 4.8-4.6 1.9 1.4.4 4.4-3.1 5.2M13.8 12c4 0 6.2 2.5 4.6 4.8-1.4 1.9-4.4.4-5.2-3.1M12 13.8c0 4-2.5 6.2-4.8 4.6-1.9-1.4-.4-4.4 3.1-5.2M10.2 12c-4 0-6.2-2.5-4.6-4.8 1.4-1.9 4.4-.4 5.2 3.1"/>',
    'ssd': '<rect x="3" y="7" width="18" height="10" rx="1.6"/><path d="M6.5 11h5M6.5 13.5h3"/>',
    'hdmi': '<path d="M3 8h18v4.5L18 16H6l-3-3.5z"/><path d="M7 11h10"/>',
    'drive': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="2.2"/>',
    'psu': '<path d="M13 2.5L5 13.5h6l-1 8 8-11h-6z"/>',
    'drift': '<circle cx="12" cy="7" r="3.5"/><path d="M12 10.5V16M5 16h14v4H5z"/>',
    'wa': '<path d="M4 20l1.3-3.9A8 8 0 1 1 8.2 19z"/><path d="M9 9.5c0 2.8 2.2 5 5 5l1.2-1.4-2-1-.8.8a3.5 3.5 0 0 1-1.8-1.8l.8-.8-1-2z"/>',
    'call': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    'store': '<path d="M4 10v10h16V10"/><path d="M3 10l2-6h14l2 6"/><path d="M10 20v-5h4v5"/>',
    'search': '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    'x': '<path d="M6 6l12 12M18 6L6 18"/>',
    'left': '<path d="M15 5l-7 7 7 7"/>',
    'right': '<path d="M9 5l7 7-7 7"/>',
    'lr': '<path d="M9 6l-6 6 6 6M15 6l6 6-6 6"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'img': '<rect x="3" y="4" width="18" height="16" rx="2.5"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-9 9"/>',
}


def icon(name: str, stroke: float = 1.8) -> str:
    """Same markup as the prototype's ic()."""
    body = IC.get(name) or IC["diagnosis"]
    sw = ("%g" % stroke)
    return mark_safe(
        f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )
