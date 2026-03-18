from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path("/home/yanshi")
OUT = ROOT / "PrivEnergyBench/docs/20min_面试汇报_詹绍基_20页图表版.pptx"

NAVY = RGBColor(21, 37, 63)
TEAL = RGBColor(35, 116, 134)
GOLD = RGBColor(191, 145, 65)
TEXT = RGBColor(34, 45, 62)
MUTED = RGBColor(96, 108, 125)
BG = RGBColor(248, 249, 251)
CARD = RGBColor(255, 255, 255)
LINE = RGBColor(214, 220, 228)

IMG = {
    "photo": ROOT / "Downloads/詹绍基证件照.jpg",
    "emb_obj": ROOT / "PrivEnergyBench/docs/redrawn_figures/emb_objective_by_mode_redraw.png",
    "emb_food": ROOT / "PrivEnergyBench/docs/redrawn_figures/emb_food_vs_energy_redraw.png",
    "emb_fixed": ROOT / "PrivEnergyBench/docs/redrawn_figures/emb_fixed_vs_plastic_redraw.png",
    "emb_heat": ROOT / "PrivEnergyBench/docs/redrawn_figures/emb_food_heatmap_redraw.png",
    "emb_raster": ROOT / "EmbodiedSNNPrototype/outputs/raster.png",
    "ns_pareto": ROOT / "PrivEnergyBench/docs/redrawn_figures/neuro_baseline_pareto_redraw.png",
    "ns_3d": ROOT / "PrivEnergyBench/docs/redrawn_figures/neuro_coupling_energy_landscape_redraw.png",
    "ns_2d": ROOT / "PrivEnergyBench/docs/redrawn_figures/neuro_coupling_threshold_energy_lines_redraw.png",
    "med_perf": ROOT / "PrivEnergyBench/docs/redrawn_figures/med_performance_redraw.png",
    "med_power": ROOT / "PrivEnergyBench/docs/redrawn_figures/med_power_latency_redraw.png",
    "med_sparse_mia": ROOT / "PrivEnergyBench/docs/redrawn_figures/med_mia_auc_redraw.png",
    "med_trans": ROOT / "PrivEnergyBench/docs/redrawn_figures/med_mia_auc_accuracy_redraw.png",
    "med_cross": ROOT / "PrivEnergyBench/docs/redrawn_figures/med_cross_tradeoff_redraw.png",
    "pe_pareto": ROOT / "PrivEnergyBench/docs/redrawn_figures/privenergy_pareto_redraw.png",
}

SECTIONS = [
    "开场",
    "个人背景",
    "项目实证",
    "方向展望",
]


def add_rect(slide, left, top, width, height, fill, line=None, radius=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    shape.line.width = Pt(0.8)
    return shape


def add_text(slide, text, left, top, width, height, *, size=20, bold=False, color=TEXT,
             font="Noto Sans CJK SC", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.name = font
    p.font.color.rgb = color
    return box


def add_bullet_list(slide, items, left, top, width, height, *, size=20, color=TEXT, bullet_color=TEAL, spacing=7):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = item
        p.font.size = Pt(size)
        p.font.name = "Noto Sans CJK SC"
        p.font.color.rgb = color
        p.space_after = Pt(spacing)
        p.bullet = True
        p.level = 0
    for p in tf.paragraphs:
        if p.runs:
            p.runs[0].font.color.rgb = color
    return box


def add_card(slide, title, body, left, top, width, height):
    add_rect(slide, left, top, width, height, CARD, LINE, radius=True)
    add_rect(slide, left, top, width, 0.16, TEAL, TEAL, radius=True)
    add_text(slide, title, left + 0.22, top + 0.24, width - 0.44, 0.42, size=16, bold=True)
    add_text(slide, body, left + 0.22, top + 0.70, width - 0.44, height - 0.92, size=13, color=MUTED)


def add_badge(slide, text, left, top, width=1.45, height=0.34, fill=GOLD, color=RGBColor(255, 255, 255)):
    add_rect(slide, left, top, width, height, fill, fill, radius=True)
    add_text(slide, text, left, top + 0.01, width, height - 0.02, size=11, bold=True, color=color, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def add_result_banner(slide, label, text, left=1.0, top=5.92, width=11.30, height=0.62):
    add_rect(slide, left, top, width, height, NAVY, NAVY, radius=True)
    add_rect(slide, left + 0.10, top + 0.10, 1.10, height - 0.20, GOLD, GOLD, radius=True)
    add_text(slide, label, left + 0.10, top + 0.12, 1.10, height - 0.24, size=10, bold=True, color=RGBColor(255, 255, 255), align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    add_text(slide, text, left + 1.38, top + 0.10, width - 1.58, height - 0.20, size=14, color=RGBColor(255, 255, 255), valign=MSO_ANCHOR.MIDDLE)


def add_source(slide, text):
    add_text(slide, text, 0.80, 6.80, 10.80, 0.15, size=8, color=MUTED)


def add_picture_contain(slide, path, left, top, width, height):
    if not Path(path).exists():
        add_text(slide, f"Missing: {Path(path).name}", left, top + height / 2 - 0.2, width, 0.4, size=14, align=PP_ALIGN.CENTER)
        return

    with Image.open(path) as img:
        img_width, img_height = img.size

    box_ratio = width / height
    img_ratio = img_width / img_height if img_height else 1

    if img_ratio >= box_ratio:
        draw_width = width
        draw_height = width / img_ratio
        draw_left = left
        draw_top = top + (height - draw_height) / 2
    else:
        draw_height = height
        draw_width = height * img_ratio
        draw_top = top
        draw_left = left + (width - draw_width) / 2

    slide.shapes.add_picture(str(path), Inches(draw_left), Inches(draw_top), width=Inches(draw_width), height=Inches(draw_height))


def add_image_panel(slide, key, left, top, width, height, caption=""):
    add_rect(slide, left, top, width, height, CARD, LINE, radius=True)
    inner_left = left + 0.12
    inner_top = top + 0.12
    inner_width = width - 0.24
    inner_height = height - 0.40
    path = IMG[key]
    if path.exists():
        add_picture_contain(slide, path, inner_left, inner_top, inner_width, inner_height)
    else:
        add_text(slide, f"Missing: {path.name}", inner_left, inner_top + inner_height / 2 - 0.2, inner_width, 0.4, size=14, align=PP_ALIGN.CENTER)
    if caption:
        add_text(slide, caption, left + 0.15, top + height - 0.23, width - 0.30, 0.18, size=10, color=MUTED, align=PP_ALIGN.CENTER)


def add_theme_frame(slide, title, subtitle, page, section_idx):
    add_rect(slide, 0, 0, 13.333, 7.5, BG, BG)
    add_rect(slide, 0, 0, 13.333, 0.74, NAVY, NAVY)
    add_rect(slide, 0.48, 0.74, 0.08, 6.12, TEAL, TEAL)
    add_text(slide, title, 0.75, 0.13, 8.2, 0.30, size=24, bold=True, color=RGBColor(255, 255, 255), font="Noto Serif CJK SC")
    if subtitle:
        add_text(slide, subtitle, 9.2, 0.16, 3.2, 0.24, size=11, color=RGBColor(226, 231, 237), align=PP_ALIGN.RIGHT)
    add_rect(slide, 0.55, 6.97, 12.20, 0.02, LINE, LINE)
    add_text(slide, f"詹绍基 | 面试汇报", 0.75, 7.00, 2.8, 0.20, size=10, color=MUTED)
    add_text(slide, f"{page:02d}", 11.95, 6.98, 0.5, 0.22, size=11, color=NAVY, bold=True, align=PP_ALIGN.RIGHT)

    nav_left = 3.95
    nav_width = 1.85
    for idx, label in enumerate(SECTIONS):
        color = TEAL if idx == section_idx else RGBColor(219, 224, 231)
        text_color = RGBColor(255, 255, 255) if idx == section_idx else MUTED
        add_rect(slide, nav_left + idx * (nav_width + 0.08), 7.00, nav_width, 0.18, color, color, radius=True)
        add_text(slide, label, nav_left + idx * (nav_width + 0.08), 7.00, nav_width, 0.18, size=9, color=text_color, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def add_title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, 0, 0, 13.333, 7.5, BG, BG)
    add_rect(slide, 0, 0, 13.333, 0.90, NAVY, NAVY)
    add_rect(slide, 0.85, 1.10, 0.10, 4.80, TEAL, TEAL)
    add_text(slide, "从医学影像到类脑智能", 1.20, 1.30, 6.4, 0.7, size=28, bold=True, color=NAVY, font="Noto Serif CJK SC")
    add_text(slide, "面向可信物理AI的研究路径", 1.20, 1.95, 6.7, 0.52, size=24, bold=True, color=TEXT, font="Noto Serif CJK SC")
    add_text(slide, "面试汇报 | 詹绍基 | 20分钟", 1.22, 2.68, 4.7, 0.3, size=14, color=MUTED)
    add_text(slide, "关键词：SNN / 世界模型 / 可解释机器人学习 / 隐私-能效-性能协同", 1.22, 3.08, 6.3, 0.4, size=13, color=TEAL)
    add_card(slide, "汇报主线", "研究动机与问题定义\n实证结果与可复现实验\n方法论与下一步计划", 1.18, 4.05, 3.45, 1.72)
    add_card(slide, "研究问题", "如何在真实约束下，让智能系统同时具备可解释性、隐私安全与能效可用性？", 4.92, 4.05, 3.55, 1.72)
    add_rect(slide, 8.55, 1.20, 3.65, 4.85, CARD, LINE, radius=True)
    if IMG["photo"].exists():
        add_picture_contain(slide, IMG["photo"], 8.72, 1.38, 3.30, 4.10)
    add_text(slide, "Suzhou University | Medical Imaging", 8.72, 5.62, 3.30, 0.2, size=10, color=MUTED, align=PP_ALIGN.CENTER)
    add_text(slide, "Research Interview Deck", 8.60, 6.40, 3.65, 0.25, size=12, color=NAVY, bold=True, align=PP_ALIGN.CENTER)


def content_slide(prs, title, subtitle, page, section_idx):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_theme_frame(slide, title, subtitle, page, section_idx)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    add_title_slide(prs)

    s = content_slide(prs, "目录", "Problem -> Evidence -> Method -> Plan", 2, 0)
    add_card(s, "01 动机与问题定义", "跨医学-法学-计算背景如何形成研究问题", 1.00, 1.45, 3.45, 1.55)
    add_card(s, "02 实证结果", "4个项目的真实图表与可复现实验链路", 4.95, 1.45, 3.45, 1.55)
    add_card(s, "03 方法论与计划", "LeCun + Sutton 框架与后续研究路线", 8.90, 1.45, 3.45, 1.55)
    add_rect(s, 1.0, 3.45, 11.35, 2.15, CARD, LINE, radius=True)
    add_text(s, "本次汇报重点", 1.28, 3.78, 2.0, 0.3, size=17, bold=True)
    add_bullet_list(s, [
        "不做概念堆砌，直接展示可验证的实验结果与下一步可执行计划。",
        "每个结论都尽量对应图表证据与可复现实验流程。",
        "前半段回答“为什么做”，后半段回答“如何做得更可靠”。",
    ], 1.28, 4.18, 10.5, 1.1, size=16)

    s = content_slide(prs, "1.1 研究问题如何形成", "From background to research question", 3, 1)
    add_rect(s, 1.00, 1.18, 7.05, 4.95, CARD, LINE, radius=True)
    add_text(s, "问题形成路径", 1.25, 1.48, 1.8, 0.3, size=17, bold=True)
    add_bullet_list(s, [
        "临床场景经验让我意识到：精度不是唯一目标，部署约束同样关键。",
        "医学训练提供了对真实任务边界的直觉，计算训练提供了实验实现能力。",
        "法学训练强化了我对隐私、责任边界与技术可治理性的关注。",
        "因此我的问题定义收敛为：在真实约束下构建可解释、节能、可信的智能系统。",
    ], 1.28, 1.92, 6.45, 3.5, size=17)
    add_rect(s, 8.55, 1.18, 3.10, 4.10, CARD, LINE, radius=True)
    if IMG["photo"].exists():
        add_picture_contain(s, IMG["photo"], 8.72, 1.36, 2.76, 3.55)
    add_text(s, "詹绍基", 8.70, 5.40, 2.85, 0.3, size=18, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, "Medical Imaging × CS × Law", 8.70, 5.72, 2.85, 0.2, size=10, color=MUTED, align=PP_ALIGN.CENTER)

    s = content_slide(prs, "1.2 跨学科训练如何转化为研究能力", "Coursework -> capability mapping", 4, 1)
    add_card(s, "医学训练", "任务约束意识：关注真实人体场景、风险边界与可部署条件", 1.00, 1.30, 3.55, 1.75)
    add_card(s, "计算训练", "实验执行能力：模型实现、评测脚本、复现实验与可视化分析", 4.88, 1.30, 3.55, 1.75)
    add_card(s, "法学训练", "治理视角：隐私保护、责任边界、规范化评测与可问责性", 8.76, 1.30, 3.55, 1.75)
    add_rect(s, 1.00, 3.55, 11.30, 2.20, CARD, LINE, radius=True)
    add_text(s, "可执行能力", 1.28, 3.88, 1.6, 0.3, size=17, bold=True)
    add_bullet_list(s, [
        "能独立完成“问题定义 -> 实验设计 -> 结果复现 -> 报告表达”全流程。",
        "能把性能、隐私、能效放在统一评测框架下分析，而非只看单一指标。",
        "能在研究早期同步考虑可解释性与部署边界，减少后期返工成本。",
        "英语能力支持持续阅读英文论文并跟进国际研究进展。",
    ], 1.28, 4.26, 10.5, 1.2, size=16)

    s = content_slide(prs, "1.3 我的真实动机", "共生 · 求真 · 不害", 5, 1)
    add_rect(s, 1.00, 1.20, 11.30, 5.30, CARD, LINE, radius=True)
    add_text(s, "我想做的不是单一模型，而是一条有价值底线的技术路线", 1.28, 1.55, 6.8, 0.38, size=21, bold=True, color=NAVY)
    add_text(s, "动机来自“共生·求真·不害”：技术应服务连接、理解现实，并守住不伤害人的底线。", 1.28, 1.98, 8.6, 0.28, size=14, color=TEAL)
    add_card(s, "医学为什么重要", "医学训练给了我两个东西：第一是仿生直觉，类脑计算本来就从生命系统中取灵感；第二是我天然会从真实人体与临床约束出发，而不是只从模型指标出发。", 1.20, 2.45, 3.35, 2.15)
    add_card(s, "法学为什么重要", "法学不是转行装饰，而是我理解技术边界的方式。做智能系统，隐私保护、责任边界、风险控制都不是附属议题，尤其在医疗和人机系统中更是核心约束。", 4.98, 2.45, 3.35, 2.15)
    add_card(s, "为什么是类脑计算", "我更关注可落地的 physical AI。相较于纯黑盒 LLM/VLA 路线，类脑、稀疏、世界模型和结构化控制更贴近节能、可解释、可验证这三件事。", 8.76, 2.45, 2.95, 2.15)
    add_result_banner(s, "Position", "我对纯 end-to-end 黑盒 VLA 保持审慎：可扩展机器人学习必须回到任务建模、几何/物理约束、规划控制与可解释评测。", left=1.20, top=5.55, width=10.90, height=0.62)

    s = content_slide(prs, "2.1 项目总览", "One continuous research chain", 6, 2)
    add_card(s, "EmbodiedSNNPrototype", "具身闭环 + 奖励调制可塑性：验证在线适应是否真正提升行为质量", 1.00, 1.30, 2.65, 1.65)
    add_card(s, "Neuro-Symbiosis", "SNN-Transformer 混合架构：观察多目标折中与耦合机制", 3.92, 1.30, 2.65, 1.65)
    add_card(s, "MedSparseSNN", "医学影像任务：把性能、隐私攻击面与能耗同时纳入评估", 6.84, 1.30, 2.65, 1.65)
    add_card(s, "PrivEnergyBench", "统一 benchmark：把不同方案放到同一坐标系可比", 9.76, 1.30, 2.65, 1.65)
    add_image_panel(s, "pe_pareto", 1.00, 3.35, 7.45, 2.55, "统一的 Pareto 评测视角")
    add_rect(s, 8.80, 3.35, 3.52, 2.55, CARD, LINE, radius=True)
    add_text(s, "学术价值", 9.08, 3.68, 1.2, 0.25, size=17, bold=True)
    add_bullet_list(s, [
        "不是分散项目，而是共享统一问题框架。",
        "从机制验证到应用评测再到基础设施，形成闭环。",
        "每一步都能自然支撑下一步研究扩展。",
    ], 9.08, 4.08, 2.8, 1.35, size=14)

    s = content_slide(prs, "2.2 EmbodiedSNN: 目标函数与模式对比", "Plasticity vs fixed strategy", 7, 2)
    add_badge(s, "Result 1", 1.00, 0.92)
    add_image_panel(s, "emb_obj", 1.00, 1.20, 5.45, 5.35, "objective by mode")
    add_image_panel(s, "emb_fixed", 6.85, 1.20, 5.45, 5.35, "fixed vs plastic")
    add_result_banner(s, "Key Takeaway", "Retuned-v3 报告中，plastic_readout 的 objective_mean 最优为 -0.4199，而 structured 为 -0.4839。")
    add_source(s, "Source [E1]: EmbodiedSNNPrototype/outputs/plasticity_compare_retuned_v3/benchmark_report.md")

    s = content_slide(prs, "2.3 EmbodiedSNN: 行为收益与资源消耗", "Reward-cost structure", 8, 2)
    add_badge(s, "Result 2", 1.00, 0.92)
    add_image_panel(s, "emb_food", 1.00, 1.20, 7.10, 4.95, "food vs energy")
    add_image_panel(s, "emb_heat", 8.45, 1.20, 3.85, 4.95, "food heatmap")
    add_result_banner(s, "Key Takeaway", "实验中出现清晰的收益-能耗权衡区间，这为后续规划与世界模型提供了可量化目标。")

    s = content_slide(prs, "2.4 EmbodiedSNN: 脉冲活动可视化", "Interpretability entry point", 9, 2)
    add_badge(s, "Result 3", 1.00, 0.92)
    add_image_panel(s, "emb_raster", 1.00, 1.28, 9.10, 5.18, "raster activity")
    add_rect(s, 10.45, 1.28, 1.87, 5.18, CARD, LINE, radius=True)
    add_text(s, "价值", 10.68, 1.66, 0.8, 0.25, size=17, bold=True)
    add_bullet_list(s, [
        "不只看最终回报。",
        "活动模式可与行为联动分析。",
        "适合作为可解释与因果分析入口。",
    ], 10.66, 2.10, 1.30, 1.6, size=13)
    add_result_banner(s, "Key Takeaway", "脉冲层面的可视化，让我可以继续把“结果好”推进到“机制清楚”。")

    s = content_slide(prs, "2.5 Neuro-Symbiosis: Pareto 前沿", "Hybrid architecture advantage", 10, 2)
    add_badge(s, "Result 4", 1.00, 0.92)
    add_image_panel(s, "ns_pareto", 1.00, 1.20, 9.10, 5.40, "Pareto baselines")
    add_rect(s, 10.45, 1.20, 1.87, 5.40, CARD, LINE, radius=True)
    add_text(s, "观察", 10.68, 1.60, 0.8, 0.25, size=17, bold=True)
    add_bullet_list(s, [
        "单一模型并不总占优。",
        "混合架构给出更合理折中。",
        "可信AI应从多目标理解。",
    ], 10.66, 2.02, 1.30, 1.8, size=13)
    add_result_banner(s, "Key Takeaway", "quick baseline_summary.csv 中，hybrid: val_acc=0.9612, mia_auc=0.4650, 呈现更均衡折中。")
    add_source(s, "Source [N1]: Neuro-Symbiosis/outputs/quick/benchmark/baseline_summary.csv")

    s = content_slide(prs, "2.6 Neuro-Symbiosis: 耦合机制", "Coupling analysis", 11, 2)
    add_badge(s, "Result 5", 1.00, 0.92)
    add_image_panel(s, "ns_3d", 1.00, 1.20, 5.45, 5.35, "3D coupling")
    add_image_panel(s, "ns_2d", 6.85, 1.20, 5.45, 5.35, "2D marginals")
    add_result_banner(s, "Key Takeaway", "耦合强度会系统性改变性能与能耗，说明这类混合架构需要自动搜索而不是手工调参。")

    s = content_slide(prs, "2.7 MedSparseSNN: 模型性能", "Medical imaging benchmarks", 12, 2)
    add_badge(s, "Result 6", 1.00, 0.92)
    add_image_panel(s, "med_perf", 1.00, 1.20, 5.45, 5.35, "model performance")
    add_image_panel(s, "med_cross", 6.85, 1.20, 5.45, 5.35, "cross-dataset tradeoff")
    add_result_banner(s, "Key Takeaway", "DermaMNIST final_compare 中，SNN test_acc=69.93±0.20，ANN=75.06±0.20；SNN latency=0.12ms/sample。")
    add_source(s, "Source [M1]: MedSparseSNN/outputs/csv/training_summary_dermamnist_final_compare.csv")

    s = content_slide(prs, "2.8 MedSparseSNN: 隐私攻击面", "Privacy risk under sparsity", 13, 2)
    add_badge(s, "Result 7", 1.00, 0.92)
    add_image_panel(s, "med_sparse_mia", 1.00, 1.30, 5.45, 5.08, "sparsity vs MIA")
    add_image_panel(s, "med_trans", 6.85, 1.30, 5.45, 5.08, "spiking-transformer vs MIA")
    add_result_banner(s, "Key Takeaway", "DermaMNIST MIA 结果中，SNN auc=0.4954±0.0005，ANN auc=0.4857±0.0016（需继续扩大样本验证显著性）。")
    add_source(s, "Source [M2]: MedSparseSNN/outputs/csv/mia_results_dermamnist_final_compare.csv")

    s = content_slide(prs, "2.9 MedSparseSNN: 能效代价", "Power and latency", 14, 2)
    add_badge(s, "Result 8", 1.00, 0.92)
    add_image_panel(s, "med_power", 1.00, 1.30, 8.20, 5.08, "power vs latency")
    add_card(s, "备注", "这页单独展示 power-latency 图，避免三图并排导致坐标轴和图例不可读。", 9.60, 1.55, 2.35, 2.10)
    add_result_banner(s, "Key Takeaway", "能效是硬约束，不是附带收益；图表必须保证可读后才有解释价值。")
    add_source(s, "Source [M3]: MedSparseSNN/outputs/csv/training_summary_dermamnist_final_compare.csv")

    s = content_slide(prs, "2.10 PrivEnergyBench: 统一评测视图", "Benchmark as research infrastructure", 15, 2)
    add_badge(s, "Result 9", 1.00, 0.92)
    add_image_panel(s, "pe_pareto", 1.00, 1.20, 9.05, 5.38, "default Pareto frontier")
    add_rect(s, 10.40, 1.20, 1.92, 5.38, CARD, LINE, radius=True)
    add_text(s, "意义", 10.66, 1.62, 0.8, 0.3, size=17, bold=True)
    add_bullet_list(s, [
        "统一坐标比较。",
        "筛选可部署解。",
        "支撑复现与搜索。",
    ], 10.62, 2.10, 1.35, 1.65, size=13)
    add_result_banner(s, "Key Takeaway", "PrivEnergyBench 默认报告显示：mlp val_acc=0.9208，linear energy=0.0164mJ/sample。")
    add_source(s, "Source [P1]: PrivEnergyBench/outputs/default/benchmark_report.md")

    s = content_slide(prs, "2.11 项目小结", "What I can already do", 16, 2)
    add_rect(s, 1.00, 1.35, 11.30, 4.95, CARD, LINE, radius=True)
    add_text(s, "到目前为止，我已经形成了一条比较完整的研究执行链路", 1.28, 1.70, 6.2, 0.4, size=21, bold=True, color=NAVY)
    add_bullet_list(s, [
        "任务定义：从真实场景约束出发，而不是只追逐流行模型。",
        "实验执行：能独立完成脚本、训练、统计、可视化与报告。",
        "结果解释：不只展示最优点，更强调 trade-off 和可复现性。",
        "下一步扩展：把世界模型、在线学习和多目标搜索接进现有链路。",
    ], 1.32, 2.40, 9.2, 2.2, size=18)
    add_card(s, "能力标签", "问题定义\n实验复现\n多目标评估\n研究延展性", 9.78, 2.18, 2.05, 2.42)

    s = content_slide(prs, "3.1 我的研究方法论", "LeCun + Sutton", 17, 3)
    add_card(s, "LeCun", "世界模型、自监督表征、长时规划。核心是学会抽象预测，而不是逐像素重建。", 1.00, 1.35, 3.55, 2.25)
    add_card(s, "Sutton", "通用方法、搜索与学习、拥抱算力扩展。核心是不要过度注入人类手工知识。", 4.88, 1.35, 3.55, 2.25)
    add_card(s, "我的理解", "架构上保持通用性，训练上追求可扩展，评测上坚持真实约束。", 8.76, 1.35, 3.55, 2.25)
    add_rect(s, 1.00, 4.10, 11.30, 1.95, CARD, LINE, radius=True)
    add_text(s, "一句话概括", 1.28, 4.45, 1.5, 0.25, size=17, bold=True)
    add_text(s, "我认同 LeCun 对世界模型和表征学习的强调，也认同 Sutton 对可扩展通用方法的坚持；我的路线是把二者放进可验证、可部署的实验框架里。", 1.28, 4.82, 10.4, 0.85, size=17, color=TEXT)

    s = content_slide(prs, "3.2 与金耀初方向的文献对接", "Topic-to-paper mapping", 18, 3)
    add_card(s, "类脑脉冲网络", "SpiLiFormer: Enhancing spiking transformers with lateral inhibition, ICCV 2025。", 1.00, 1.30, 5.35, 1.35)
    add_card(s, "具身智能", "Morphology evolution for embodied robot design with a classifier-guided diffusion model, IEEE TEVC 2025 (accepted)。", 6.85, 1.30, 5.35, 1.35)
    add_card(s, "联邦与隐私", "Federated many-task Bayesian optimization, IEEE TEVC 2024；DP-FSAEA: Differential privacy for federated surrogate-assisted EAs, IEEE TEVC 2024。", 1.00, 3.00, 5.35, 1.35)
    add_card(s, "可信与可扩展", "Knowledge-empowered, collaborative, and co-evolving AI models: The post-LLM roadmap, Engineering 2024。", 6.85, 3.00, 5.35, 1.35)
    add_rect(s, 1.00, 4.92, 11.20, 1.20, CARD, LINE, radius=True)
    add_text(s, "对接结论", 1.28, 5.24, 1.3, 0.2, size=16, bold=True)
    add_text(s, "我的项目线（SNN/隐私-能效-性能评测/多目标优化）可以和实验室近期文献形成可执行的课题衔接。", 2.60, 5.24, 8.6, 0.22, size=16)
    add_source(s, "Source [J1-J5]: en.westlake.edu.cn/about/faculty/engineering/jin-pub_year.html")

    s = content_slide(prs, "3.3 拟开展工作 I", "World model for embodied SNN", 19, 3)
    add_rect(s, 1.00, 1.30, 11.30, 5.20, CARD, LINE, radius=True)
    add_text(s, "方向一：把 JEPA 式抽象预测引入具身 SNN", 1.28, 1.66, 5.2, 0.3, size=20, bold=True, color=NAVY)
    add_bullet_list(s, [
        "目标：提升长时决策稳定性与跨场景泛化。",
        "实验设计：无世界模型 / 像素预测 / 表征预测 三路线对比。",
        "评测指标：任务回报、能耗、OOD 鲁棒性、迁移表现。",
        "预期贡献：让具身 SNN 从“会动”走向“会规划”。",
    ], 1.32, 2.24, 6.8, 2.25, size=18)
    add_card(s, "为什么值得做", "这条线能把我现有的具身实验和 LeCun 的世界模型方法真正接起来。", 8.95, 2.02, 2.35, 1.55)
    add_card(s, "风险控制", "先在小环境验证，再逐步扩大状态复杂度。", 8.95, 3.96, 2.35, 1.20)

    s = content_slide(prs, "3.4 拟开展工作 II", "Trustworthy neuromorphic systems", 20, 3)
    add_rect(s, 1.00, 1.30, 11.30, 5.20, CARD, LINE, radius=True)
    add_text(s, "方向二：可信与隐私约束下的类脑系统", 1.28, 1.66, 5.2, 0.3, size=20, bold=True, color=NAVY)
    add_bullet_list(s, [
        "在联邦或分布式设置中评估 SNN-Transformer 混合架构。",
        "把 MIA、DP 预算、能耗成本一起纳入统一目标。",
        "使用多目标优化或进化搜索自动发现更优配置。",
        "产出不仅是论文结果，也包括可复用 benchmark 与部署建议。",
    ], 1.32, 2.24, 6.9, 2.20, size=18)
    add_card(s, "为什么适合实验室", "它同时贴合 trustworthy AI、SNN 和多目标优化三条主线。", 8.92, 2.04, 2.38, 1.52)
    add_card(s, "我的优势", "我已经把三目标评测与图表链路搭起来了。", 8.92, 3.94, 2.38, 1.22)

    s = content_slide(prs, "3.5 参考文献（节选）", "Key references used in this deck", 21, 3)
    add_rect(s, 1.00, 1.25, 11.30, 5.35, CARD, LINE, radius=True)
    add_bullet_list(s, [
        "[E1] EmbodiedSNNPrototype benchmark report (retuned_v3), objective/food/energy statistics.",
        "[N1] Neuro-Symbiosis baseline summary (quick benchmark).",
        "[M1-M3] MedSparseSNN final compare + MIA CSV + power-latency figure.",
        "[P1] PrivEnergyBench default benchmark report (multi-seed aggregate).",
        "[J1-J5] Yaochu Jin publication list (2024-2025, Westlake).",
        "[L1] LeCun, A Path Towards Autonomous Machine Intelligence, 2022.",
        "[S1] Sutton, The Bitter Lesson, 2019.",
        "[V1] RT-2 (Brohan et al., 2023), [V2] RT-X (Open X-Embodiment, 2023), [V3] OpenVLA (Kim et al., 2024).",
    ], 1.25, 1.70, 10.7, 4.3, size=14)

    s = content_slide(prs, "3.6 结束页", "Why me", 22, 3)
    add_rect(s, 1.00, 1.25, 11.30, 5.35, CARD, LINE, radius=True)
    add_text(s, "为什么我适合进入这个方向继续做", 1.28, 1.68, 5.0, 0.35, size=22, bold=True, color=NAVY)
    add_bullet_list(s, [
        "能独立完成从实验搭建、结果统计到图表复现的研究闭环。",
        "研究重点稳定在可解释、可信、可部署的类脑与隐私优化方向。",
        "已有项目与实验室文献方向存在明确技术接缝，可直接进入执行阶段。",
        "后续将以可复现协议和可验证指标作为工作标准。",
    ], 1.32, 2.34, 7.3, 2.3, size=18)
    add_card(s, "最后一句", "我带来的不是一串零散项目，而是一条已经开始成形的研究路线。", 8.92, 2.28, 2.60, 1.82)
    add_text(s, "感谢各位老师，欢迎批评指正", 1.30, 5.82, 10.6, 0.3, size=18, color=TEAL, align=PP_ALIGN.CENTER)

    prs.save(str(OUT))
    print(f"saved: {OUT}")


if __name__ == "__main__":
    build()
