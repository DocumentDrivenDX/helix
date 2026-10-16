"""Build the team's static review handout from the retained spike screenshots."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'output/pdf/helix-architecture-diagram-review.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
FONTROOT=Path('/System/Library/Fonts/Supplemental')
if (FONTROOT/'Arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('ReviewSans',str(FONTROOT/'Arial.ttf')))
    pdfmetrics.registerFont(TTFont('ReviewSansBold',str(FONTROOT/'Arial Bold.ttf')))
    pdfmetrics.registerFontFamily('ReviewSans',normal='ReviewSans',bold='ReviewSansBold',italic='ReviewSans',boldItalic='ReviewSansBold')
    NORMAL,BOLD='ReviewSans','ReviewSansBold'
else:
    NORMAL,BOLD='Helvetica','Helvetica-Bold'
W,H=960,640
INK='#172B42';MUTED='#516579';BLUE='#245E9C';GROUND='#F8FAFC'
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('HELIX architecture diagrams - team review')
c.setAuthor('HELIX')
c.setSubject('Six diagram approaches, source provenance, integration findings, and feedback questions')
styles={
 'body':ParagraphStyle('body',fontName=NORMAL,fontSize=11,leading=15,textColor=HexColor(INK)),
 'small':ParagraphStyle('small',fontName=NORMAL,fontSize=9.5,leading=13,textColor=HexColor(MUTED)),
 'note':ParagraphStyle('note',fontName=NORMAL,fontSize=10.5,leading=14,textColor=HexColor(INK)),
}
page_number=0

def para(text,x,top,width,kind='body'):
    p=Paragraph(text,styles[kind]);w,h=p.wrap(width,H)
    assert top-h>=35,('Text would cross footer',text[:60],top,h)
    p.drawOn(c,x,top-h)
    return top-h

def line(x,y,text,size=12,bold=False,color=INK):
    c.setFillColor(HexColor(color));c.setFont(BOLD if bold else NORMAL,size);c.drawString(x,y,text)

def start(title,subtitle=None):
    global page_number
    page_number+=1
    c.setFillColor(HexColor(GROUND));c.rect(0,0,W,H,stroke=0,fill=1)
    line(44,H-34,'HELIX / DIAGRAM EXPLORATION',9,bold=True,color=BLUE)
    line(44,H-72,title,27,bold=True)
    if subtitle:para(subtitle,44,H-88,W-88,'small')
    c.setStrokeColor(HexColor('#CAD6E2'));c.setLineWidth(.6);c.line(44,35,W-44,35)
    line(44,20,'Team feedback draft | 15 October 2026',8.5,color=MUTED)
    c.setFont(NORMAL,8.5);c.drawRightString(W-44,20,f'{page_number:02d} / 09')

def end():c.showPage()

def image(name,x=44,y=185,maxw=872,maxh=330):
    reader=ImageReader(str(HERE/name));iw,ih=reader.getSize();scale=min(maxw/iw,maxh/ih)
    w,h=iw*scale,ih*scale
    c.drawImage(reader,x+(maxw-w)/2,y+(maxh-h)/2,width=w,height=h,mask='auto')

def example(title,subtitle,name,origin,tested,source):
    start(title,subtitle);image(name)
    line(44,166,'WHERE IT CAME FROM',9,bold=True,color=BLUE)
    line(498,166,'WHAT WE OBSERVED',9,bold=True,color=BLUE)
    para(origin,44,154,418,'note');para(tested,498,154,418,'note')
    para(source,44,57,872,'small');end()

start('Architecture diagrams for HELIX','Six approaches, one shared architecture. Review the visual results before choosing a standard.')
para('We are exploring how HELIX can produce clear solution diagrams for conference talks, developer onboarding, and reference documentation. The examples preserve the same six entities and relationships; differences in layout, typography, and interaction are deliberate.',44,477,872)
line(44,410,'APPROACH',10,bold=True,color=BLUE);line(310,410,'HOW IT WAS MADE',10,bold=True,color=BLUE);line(605,410,'REVIEW FOCUS',10,bold=True,color=BLUE)
rows=[('1. Infographic Architect','Prompt-guided, hand-authored SVG','Composition and visible layout defects'),('2. Eraser Diagrams','Native components and connector routing','Clean geometry and editability'),('3. D2 / TALA','Declarative source with pinned positions','Layout control and revision effort'),('4. Visual Explainer','Prompt-guided HTML/SVG walkthrough','Visual style and explanatory focus'),('5. Beautiful Mermaid','Generated directly from Mermaid text','Maintainable documentation baseline'),('6. Integrated prototype','Eraser output + Visual Explainer style','Can the strengths work together?')]
y=385
for a,b,d in rows:
    c.setStrokeColor(HexColor('#DFE6ED'));c.line(44,y-14,916,y-14)
    line(44,y,a,11,bold=True);line(310,y,b,10.5);line(605,y,d,10.5);y-=38
para('<b>Please judge the image first:</b> what do you understand after a brief look, and what is hard to follow? Then consider how easily we could maintain it. The integration is a feasibility prototype, not an adopted HELIX standard.',44,133,872)
para('Reading note: pages 2-7 show the six overview examples. Page 8 captures the integrated walkthrough in an active step. Page 9 lists sources and feedback questions. Static PDF captures cannot demonstrate interaction.',44,78,872,'small');end()

example('1. Infographic Architect','Original spike | Prompt-guided editable SVG','01-infographic-architect.png',
 'Based on SizeSStudio\'s architecture-infographic skill, visual grammar, template catalog, and QA guidance. The three-column methodology pattern was adapted to HELIX. Geometry was authored locally; this was not an automatic layout engine.',
 'The composition separates runtime, HELIX, and project documents. It also retains the crowded labels and ambiguous document-stack outlines identified in review. Those defects are shown rather than hidden in this comparison.',
 'Source: <link href="https://github.com/SizeSStudio/infographic-architect" color="#245E9C">github.com/SizeSStudio/infographic-architect</link> | Source snapshot b3dd7e5')
example('2. Eraser Diagrams','Native renderer | Components, measured text, and routed connectors','02-eraser.png',
 'Rendered with the open-source Eraser Diagrams Node package. The source is structured JSON with native groups, shapes, text, and relationships. Stock components were restyled with plain fills and an emphasized routing skill.',
 'The renderer measures component bounds and routes connections around them. This example returned no renderer warnings. It is cleaner geometrically, although the stock treatment needs more art direction for a conference presentation.',
 'Source: <link href="https://github.com/eraserlabs/eraser-diagrams" color="#245E9C">github.com/eraserlabs/eraser-diagrams</link> | @eraserlabs/diagrams 0.2.0')
example('3. D2 / TALA','Declarative source | Positioned composition, TALA routing','03-d2-tala.png',
 'Produced with D2 0.9.0 and its TALA layout engine. An initial automatic layout was retained in the source bundle. The version shown pins entity positions while the engine handles rendering and connector routing.',
 'The first automatic result was tall and poorly suited to a slide. Position constraints produced a usable landscape arrangement. This supports deliberate layout control; it does not show that automatic layout alone meets the presentation goal.',
 'Sources: <link href="https://github.com/d2lang/d2" color="#245E9C">github.com/d2lang/d2</link> and <link href="https://d2lang.com/tour/tala/" color="#245E9C">d2lang.com/tour/tala/</link> | D2 0.9.0')
example('4. Visual Explainer','Prompt-guided HTML/SVG | Dark Blueprint style and step-by-step focus','04-visual-explainer.png',
 'Authored using nicobailon\'s Visual Explainer skill, Blueprint style register, and diagram guidance. The local HTML contains editable SVG and controls that highlight each of the six relationships. This was prompt-guided authoring.',
 'The dark palette, warm focal accent, and active-path walkthrough were preferred in the initial review. The original figure still relied on manual geometry. This PDF shows the overview; the HTML also provides six-step interaction.',
 'Source: <link href="https://github.com/nicobailon/visual-explainer" color="#245E9C">github.com/nicobailon/visual-explainer</link> | Source snapshot 69cd739')
example('5. Beautiful Mermaid','Generated SVG | A low-effort documentation baseline','05-beautiful-mermaid.png',
 'Generated from a short Mermaid definition using the beautiful-mermaid package. The renderer provides coordinated colors and automatic layout. The skill and catalog were explicitly declared inside the HELIX subgraph.',
 'Text-source maintenance is simple, but the result is very wide with thin connectors and relatively small labels. It is useful as a reference baseline. Its aspect ratio is retained here so the presentation tradeoff is visible.',
 'Source: <link href="https://github.com/lukilabs/beautiful-mermaid" color="#245E9C">github.com/lukilabs/beautiful-mermaid</link> | beautiful-mermaid 1.1.3')
example('6. Integrated prototype','Visual Explainer presentation + Eraser native geometry','06-hybrid.png',
 'The Eraser JSON was styled with Visual Explainer\'s dark Blueprint palette and rendered by Eraser. The native rendered elements, measured labels, and routed paths were retained. A local HTML wrapper adds captions and six-step controls.',
 'The integration preserves geometry while changing emphasis. A governance return path needed an authored perimeter guide to avoid a connector crossing. Eraser still owns measurement and rendering; the walkthrough does not redraw the diagram.',
 'Combined sources: Eraser Diagrams 0.2.0 + Visual Explainer guidance | Local feasibility prototype')
example('Integrated walkthrough: an active relationship','Step 5 of 6 | Author and reconcile project documents','06-hybrid-step.png',
 'This is a screenshot of the same integrated HTML at one active step. Controls select relationships by stable Eraser element IDs. Only opacity, color, border emphasis, and external captions change.',
 'All six steps and the Overview reset were exercised. Entity geometry remained unchanged and label-to-box overlap checks found none. The static PDF cannot reproduce these controls; the editable HTML remains the interactive prototype.',
 'Evidence: local browser checks, measured Eraser geometry, and retained HTML source | No audience-comprehension or venue-projection test yet')

start('Feedback and source references','Please review visual quality and maintenance practicality as separate questions.')
left=44;top=478
questions=[('Reading','What is HELIX, what belongs inside it, and how does a request become a governing document?'),('Geometry','Which labels or connectors are crowded, ambiguous, or difficult to trace?'),('Presentation','Would you use the integrated dark diagram in a public talk? What would you change first?'),('Onboarding','Does stepping through one relationship at a time help, or would progressive reveal work better?'),('Maintenance','Should HELIX favor editable native diagrams, concise text source, or different outputs for different audiences?')]
for label,q in questions:
    line(left,top,label.upper(),9,bold=True,color=BLUE);top=para(q,left,top-10,420,'note')-17
line(510,478,'SOURCE PROJECTS',10,bold=True,color=BLUE)
sources=[('Infographic Architect','https://github.com/SizeSStudio/infographic-architect'),('Eraser Diagrams','https://github.com/eraserlabs/eraser-diagrams'),('D2 / TALA','https://d2lang.com/tour/tala/'),('Visual Explainer','https://github.com/nicobailon/visual-explainer'),('Beautiful Mermaid','https://github.com/lukilabs/beautiful-mermaid'),('C4 diagram review checklist','https://c4model.com/diagrams/checklist')]
y=453
for title,url in sources:
    line(510,y,title,11,bold=True)
    y=para(f'<link href="{url}" color="#245E9C">{escape(url.removeprefix("https://"))}</link>',510,y-10,406,'small')-16
para('The C4 checklist informed semantic review; it is not a renderer. These are conceptual solution views, not strict C4 container diagrams. Upstream projects did not create or endorse the HELIX examples.',44,139,872,'small')
para('Feedback format: name the example and page, identify a concrete strength or defect, and say whether it affects comprehension, visual polish, or future editing. The original SVG/JSON/HTML/D2/Mermaid files are retained with the spike notes.',44,91,872,'small');end()
c.save()
print(OUT)
