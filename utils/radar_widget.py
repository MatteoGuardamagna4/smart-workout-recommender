"""
Custom Radar/Spider Chart Widget for Streamlit.
A fully custom HTML/CSS/JS component rendered via st.components.v1.html().
Displays an animated radar chart of the user's fitness profile with:
- SVG-based radar with gradient fill
- Smooth CSS animation on load
- Hover tooltips showing exact values
- Responsive design
- Comparison overlay (user vs cluster average)

Usage:
    from utils.radar_widget import render_fitness_radar
    render_fitness_radar(user_scores, cluster_scores, labels)
"""

import streamlit.components.v1 as components
import json


def render_fitness_radar(
    user_scores: dict,
    cluster_scores: dict | None = None,
    height: int = 480,
    title: str = "Your Fitness Profile"
):
    """
    Render an animated radar chart comparing user profile vs cluster average.

    Args:
        user_scores: Dict of {label: score} where score is 0-100.
                     e.g. {"Strength": 70, "Endurance": 55, ...}
        cluster_scores: Optional dict with same keys for cluster average overlay.
        height: Widget height in pixels.
        title: Chart title.
    """
    labels = list(user_scores.keys())
    user_values = list(user_scores.values())
    cluster_values = list(cluster_scores.values()) if cluster_scores else None

    data_json = json.dumps({
        "labels": labels,
        "userValues": user_values,
        "clusterValues": cluster_values,
        "title": title
    })

    html_code = _build_html(data_json)
    components.html(html_code, height=height + 60, scrolling=False)


def _build_html(data_json: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: transparent;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100%;
    }}
    .radar-container {{
        position: relative;
        width: 100%;
        max-width: 520px;
        margin: 0 auto;
        text-align: center;
    }}
    .radar-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: #1E3A5F;
        margin-bottom: 8px;
    }}
    .radar-svg {{
        width: 100%;
        height: auto;
    }}
    /* Animation: user polygon draws in */
    .user-polygon {{
        animation: radarFadeIn 1s ease-out forwards;
        opacity: 0;
    }}
    @keyframes radarFadeIn {{
        0% {{ opacity: 0; transform: scale(0.3); }}
        60% {{ opacity: 0.8; transform: scale(1.05); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    .cluster-polygon {{
        animation: clusterFadeIn 1.2s ease-out 0.4s forwards;
        opacity: 0;
    }}
    @keyframes clusterFadeIn {{
        0% {{ opacity: 0; }}
        100% {{ opacity: 1; }}
    }}
    /* Tooltip */
    .radar-tooltip {{
        position: absolute;
        background: rgba(30, 58, 95, 0.92);
        color: #fff;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.82rem;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.2s;
        white-space: nowrap;
        z-index: 10;
    }}
    .radar-tooltip.visible {{
        opacity: 1;
    }}
    /* Legend */
    .radar-legend {{
        display: flex;
        justify-content: center;
        gap: 24px;
        margin-top: 8px;
        font-size: 0.85rem;
        color: #4B5563;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .legend-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }}
    .legend-dot.user {{ background: rgba(102, 126, 234, 0.8); }}
    .legend-dot.cluster {{ background: rgba(245, 158, 66, 0.6); }}
    /* Data points pulse on hover */
    .data-point {{
        transition: r 0.2s ease, fill 0.2s ease;
        cursor: pointer;
    }}
    .data-point:hover {{
        r: 7;
    }}
</style>
</head>
<body>
<div class="radar-container" id="radarContainer">
    <div class="radar-title" id="radarTitle"></div>
    <svg class="radar-svg" id="radarSvg" viewBox="0 0 400 430"></svg>
    <div class="radar-legend" id="radarLegend"></div>
    <div class="radar-tooltip" id="radarTooltip"></div>
</div>

<script>
(function() {{
    const data = {data_json};
    const labels = data.labels;
    const userValues = data.userValues;
    const clusterValues = data.clusterValues;
    const n = labels.length;

    // SVG config
    const cx = 200, cy = 200;
    const maxR = 150;
    const levels = 5;
    const angleStep = (2 * Math.PI) / n;
    const startAngle = -Math.PI / 2; // Start from top

    const svg = document.getElementById('radarSvg');
    const tooltip = document.getElementById('radarTooltip');
    const container = document.getElementById('radarContainer');

    document.getElementById('radarTitle').textContent = data.title;

    // ── Helper: polar to cartesian ──
    function polarToXY(angle, radius) {{
        return {{
            x: cx + radius * Math.cos(angle),
            y: cy + radius * Math.sin(angle)
        }};
    }}

    // ── Draw grid rings ──
    for (let lvl = 1; lvl <= levels; lvl++) {{
        const r = (maxR / levels) * lvl;
        const points = [];
        for (let i = 0; i < n; i++) {{
            const angle = startAngle + i * angleStep;
            const p = polarToXY(angle, r);
            points.push(`${{p.x}},${{p.y}}`);
        }}
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', points.join(' '));
        polygon.setAttribute('fill', lvl % 2 === 0 ? 'rgba(102,126,234,0.04)' : 'rgba(102,126,234,0.08)');
        polygon.setAttribute('stroke', 'rgba(102,126,234,0.15)');
        polygon.setAttribute('stroke-width', '1');
        svg.appendChild(polygon);

        // Level label
        if (lvl < levels) {{
            const val = Math.round((100 / levels) * lvl);
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', cx + 4);
            text.setAttribute('y', cy - r + 12);
            text.setAttribute('font-size', '10');
            text.setAttribute('fill', '#9CA3AF');
            text.textContent = val;
            svg.appendChild(text);
        }}
    }}

    // ── Draw axes + labels ──
    for (let i = 0; i < n; i++) {{
        const angle = startAngle + i * angleStep;
        const pEnd = polarToXY(angle, maxR);

        // Axis line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', cx);
        line.setAttribute('y1', cy);
        line.setAttribute('x2', pEnd.x);
        line.setAttribute('y2', pEnd.y);
        line.setAttribute('stroke', 'rgba(102,126,234,0.2)');
        line.setAttribute('stroke-width', '1');
        svg.appendChild(line);

        // Label
        const pLabel = polarToXY(angle, maxR + 22);
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pLabel.x);
        text.setAttribute('y', pLabel.y);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', '600');
        text.setAttribute('fill', '#374151');
        text.textContent = labels[i];
        svg.appendChild(text);
    }}

    // ── Draw data polygon ──
    function drawDataPolygon(values, fillColor, strokeColor, className) {{
        const points = [];
        for (let i = 0; i < n; i++) {{
            const angle = startAngle + i * angleStep;
            const r = (values[i] / 100) * maxR;
            const p = polarToXY(angle, r);
            points.push(`${{p.x}},${{p.y}}`);
        }}
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', points.join(' '));
        polygon.setAttribute('fill', fillColor);
        polygon.setAttribute('stroke', strokeColor);
        polygon.setAttribute('stroke-width', '2.5');
        polygon.setAttribute('class', className);
        svg.appendChild(polygon);
        return points;
    }}

    // ── Draw cluster average (behind user) ──
    if (clusterValues) {{
        drawDataPolygon(
            clusterValues,
            'rgba(245, 158, 66, 0.15)',
            'rgba(245, 158, 66, 0.7)',
            'cluster-polygon'
        );
    }}

    // ── Draw user polygon ──
    drawDataPolygon(
        userValues,
        'rgba(102, 126, 234, 0.25)',
        'rgba(102, 126, 234, 0.9)',
        'user-polygon'
    );

    // ── Draw data points with hover ──
    for (let i = 0; i < n; i++) {{
        const angle = startAngle + i * angleStep;
        const r = (userValues[i] / 100) * maxR;
        const p = polarToXY(angle, r);

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', p.x);
        circle.setAttribute('cy', p.y);
        circle.setAttribute('r', '5');
        circle.setAttribute('fill', 'rgba(102, 126, 234, 0.9)');
        circle.setAttribute('stroke', '#fff');
        circle.setAttribute('stroke-width', '2');
        circle.setAttribute('class', 'data-point user-polygon');

        // Tooltip events
        circle.addEventListener('mouseenter', (e) => {{
            let text = `${{labels[i]}}: ${{userValues[i]}}`;
            if (clusterValues) {{
                text += ` (avg: ${{clusterValues[i]}})`;
            }}
            tooltip.textContent = text;
            tooltip.classList.add('visible');

            const rect = container.getBoundingClientRect();
            const svgRect = svg.getBoundingClientRect();
            const scaleX = svgRect.width / 400;
            const scaleY = svgRect.height / 400;
            tooltip.style.left = (p.x * scaleX - tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = (p.y * scaleY - 36 + (svgRect.top - rect.top)) + 'px';
        }});
        circle.addEventListener('mouseleave', () => {{
            tooltip.classList.remove('visible');
        }});

        svg.appendChild(circle);
    }}

    // ── Legend ──
    const legend = document.getElementById('radarLegend');
    let legendHTML = '<div class="legend-item"><div class="legend-dot user"></div>You</div>';
    if (clusterValues) {{
        legendHTML += '<div class="legend-item"><div class="legend-dot cluster"></div>Cluster Average</div>';
    }}
    legend.innerHTML = legendHTML;
}})();
</script>
</body>
</html>
"""
