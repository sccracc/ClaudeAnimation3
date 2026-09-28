from .core import *
from .scene import *
from .assets import *
from .figure import Figure

def brain_icon(ctx, x, y, r, a=1.0, seed=0):
    pts = ellipse_pts(x, y, r * 1.15, r * .8, 50, -.05)
    paper_shape(ctx, pts, BLUSH, a, seed=seed, shadow=.15, grain=.8)
    paper_shape(ctx, ellipse_pts(x - r * .7, y + r * .62, r * .42, r * .28, 30, .3), mix(BLUSH, RED_L, .4), a, seed=seed + 1, shadow=.08)
    for k in range(6):
        rr = .82 - k * .13
        sq = [(x + math.cos(a0) * r * 1.1 * rr + math.sin(a0 * 9 + k) * r * .06, y + math.sin(a0) * r * .75 * rr + math.cos(a0 * 9 + k * 2) * r * .06)
              for a0 in [-2.9 + j * .16 + k * .3 for j in range(22 - k * 2)]]
        ink(ctx, catmull(sq, 3), 1.6, RED_D, .5 * a, seed=seed + k)
    ink(ctx, pts, 2, RED_D, .7 * a, seed=seed + 9, closed=True)

class Contraction(Scene):
    sid = "s03_contraction"
    extra = 0.8

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        zA = c("calcium", 2) - 1.0      # into the filaments
        zB = c("millions") - .5         # out to the sarcomere
        zC = c("whole") - .6            # out to the arm
        def L1(ctx): self.signal(ctx, t)
        def L2(ctx): self.closeup(ctx, t)
        def L3(ctx): self.sarc(ctx, t)
        def L4(ctx): self.arm(ctx, t)
        if t < zA + 1.3:
            zoom_through(ctx, t, zA, 1.3, (1400, 560), L1, L2, zmax=6, bg_t=t)
        elif t < zB + 1.3:
            zoom_out(ctx, t, zB, 1.3, (960, 540), L2, L3, zmax=4, bg_t=t)
        else:
            zoom_out(ctx, t, zC, 1.2, (870, 600), L3, L4, zmax=5, bg_t=t)
        chapter_tag(ctx, t, 2, "How a contraction works")

    def sfx(self):
        c = self.cue
        return [(c("calcium", 2) - 1.0, 'zoom'), (c("millions") - .5, 'zoomout'), (c("whole") - .6, 'zoomout')]

    # -------------------------------------------------- nerve -> fiber -> calcium
    def signal(self, ctx, t):
        c = self.cue
        tz = c("at") - .3
        cam = keys(t, [(0, (960, 540, 1.0)), (tz, (960, 540, 1.0)), (tz + 1.4, (1400, 600, 1.5))])
        ctx.save(); camera(ctx, *cam)
        bx, by = 330, 300
        brain_icon(ctx, bx, by, 135, ph(t, 0, .8), seed=600)
        # spinal cord
        sc_pts = catmull([(bx + 20, by + 100), (bx + 40, by + 250), (bx + 30, by + 420), (bx + 40, 1000)], 10)
        ink(ctx, sc_pts, 26, mix(PAPER_D, SLATE_L, .5), ph(t, .2, .8), prog=ph(t, .2, 1.2, ease), seed=601, sketch=False)
        ink(ctx, sc_pts, 1.6, INK_SOFT, .6 * ph(t, .2, .8), prog=ph(t, .2, 1.2, ease), seed=602)
        # motor neuron cell body + axon
        cbx, cby = bx + 45, 700
        na = ph(t, c("brain") - .3, .6)
        if na > 0:
            for k in range(7):
                ang = k * .9 + .3
                ink(ctx, catmull([(cbx, cby), (cbx + math.cos(ang) * 40, cby + math.sin(ang) * 40), (cbx + math.cos(ang + .3) * 70, cby + math.sin(ang + .3) * 70)], 5), 2.4, OCHRE, na, seed=610 + k, sketch=False)
            blob(ctx, cbx, cby, 26, OCHRE_L, na, seed=611, outline=hexc('9A6420'), ow=1.6)
            dots(ctx, [(cbx, cby)], 8, hexc('9A6420'), na)
        axon = catmull([(cbx + 20, cby), (600, cby - 40), (820, cby + 30), (1000, 560), (1110, 520)], 12)
        ink(ctx, axon, 7, OCHRE, na, prog=ph(t, c("brain"), 1.2, ease), seed=620)
        # fiber
        fiber_tube(ctx, 1080, 1900, 600, 190, ph(t, .3, .8), seed=630, stri_sp=12)
        # neuromuscular junction terminals
        ja = ph(t, c("brain") + 1.0, .5)
        for k in range(3):
            ink(ctx, [(1110, 520), (1135 + k * 26, 526 + k * 8)], 3.4, OCHRE, ja, seed=640 + k, sketch=False)
            dots(ctx, [(1135 + k * 26, 526 + k * 8)], 7, OCHRE_L, ja)
        # travelling signal: brain -> cord -> axon
        route = [(bx, by)] + sc_pts[:int(len(sc_pts) * .65)] + axon
        for k in range(3):
            st = c("sends") + k * .45
            pp = (t - st) / 1.6
            if 0 <= pp <= 1:
                x, y = point_at(route, pp); glow(ctx, x, y, 70, OCHRE_L); dots(ctx, [(x, y)], 7, CREAM)
        label(ctx, "brain", bx + 170, by - 110, bx + 80, by - 60, t, c("brain") - .2, size=40, seed=1)
        label(ctx, "spinal cord", bx - 180, 860, bx + 30, 800, t, c("brain") + .4, size=36, seed=2, align='left')
        label(ctx, "motor neuron", 560, 860, 640, cby - 30, t, c("motor") - .2, font='serif_i', size=48, seed=3, a=1 - ph(t, tz - .3, .4))
        label(ctx, "nerve meets muscle", 1150, 420, 1150, 525, t, c("at") + .2, size=36, seed=6, align='left')
        # wave sweeping across the fiber
        wv = ph(t, c("sweeps") - .2, 1.4, ease)
        if 0 < wv < 1:
            for sgn in (-1, 1):
                x = 1200 + sgn * wv * 700
                if 1150 < x < 1900: glow(ctx, x, 560, 120, OCHRE_L, (1 - wv) * 1.2)
        # SR stores + calcium release
        sa = ph(t, c("releases") - .5, .6)
        if sa > 0:
            for k in range(6):
                xx = 1200 + k * 120
                ink(ctx, [(xx, 530), (xx + 30, 565), (xx - 10, 600), (xx + 25, 640), (xx, 665)], 2.2, TEAL, sa * .8, seed=650 + k)
            label(ctx, "calcium stores", 1560, 400, 1455, 560, t, c("stores") - .3, size=36, seed=4)
        ca = ph(t, c("calcium") - .1, 1.2, eout)
        if ca > 0:
            rng = np.random.default_rng(3)
            for k in range(40):
                sx = 1200 + (k % 6) * 120 + 10; sy = 600
                ang = rng.random() * 6.28; d = 20 + rng.random() * 55
                x = sx + math.cos(ang) * d * ca; y = sy + math.sin(ang) * d * .8 * ca
                blob(ctx, x, y, 7, TEAL_L, ca, seed=660 + k, shadow=.1, outline=TEAL, ow=1.1)
            text(ctx, "Ca²⁺", 1760, 790, 'sans_b', 40, TEAL, ca, 'center')
            label(ctx, "calcium", 1520, 800, 1470, 640, t, c("calcium") + .2, font='serif_i', size=44, c=TEAL, seed=5)
        ctx.restore()

    # -------------------------------------------------- cross-bridge close-up
    def cycle(self, t):
        """returns (k, u): stroke count and phase within current cycle"""
        c = self.cue
        t0 = c("latch") - .25; per = 1.7
        if t < t0: return 0, -1
        x = (t - t0) / per
        return int(x), x - int(x)

    def closeup(self, ctx, t):
        c = self.cue
        h = 140            # vertical distance head base -> actin
        yA, yM = 360, 360 + h + 70
        k, u = self.cycle(t)
        # head angle / attachment per phase
        def head_state(u):
            if u < 0: return 50, False, 0
            if u < .15: return 50, ease(u / .15) > .5, 0            # attach
            if u < .45: return lerp(50, 112, ease((u - .15) / .3)), True, ease((u - .15) / .3)  # power stroke
            if u < .58: return 112, False, 1           # release (ATP bound)
            return lerp(112, 50, ease((u - .58) / .42)), False, 1   # re-cock
        th, att, sp = head_state(u)
        cot = lambda d: math.cos(math.radians(d)) / math.sin(math.radians(d))
        stroke_len = h * (cot(50) - cot(112))
        slide = -(k * stroke_len + (sp if u >= 0 else 0) * stroke_len) if u >= 0 else 0
        slide = slide + (0 if u < 0 else 0)
        # actin (large) sliding left toward the M-line
        blocked = 1 - ph(t, c("uncovers") - .2, 1.0, ease)
        sites = ph(t, c("binding") - .2, .6)
        ctx.save(); ctx.translate(slide % (stroke_len * 3) if False else slide, 0)
        actin(ctx, -800, 2900, yA, 1, seed=700, bead=13, sites=sites, blocked=blocked)
        ctx.restore()
        # calcium bound to the regulatory proteins
        cal = ph(t, c("calcium", 2) - .5, .6) * (1 - ph(t, c("millions") - 1, .5))
        if cal > 0:
            for j in range(6):
                x = 120 + j * 330 + (slide % 330 if False else 0)
                blob(ctx, x + ((slide) % 330), yA - 48, 11, TEAL_L, cal, seed=710 + j, outline=TEAL, ow=1.2)
        # thick filament
        paper_shape(ctx, rrect_pts(-100, yM - 26, 2200, 52, 26), RED_D, 1, seed=720, shadow=.2, grain=.9, shade=.2)
        heads_x = [260, 590, 920, 1250, 1580]
        for i, bx in enumerate(heads_x):
            by = yM - 26
            L = h / math.sin(math.radians(th)) if att else (h - 28) / math.sin(math.radians(th))
            hx = bx + math.cos(math.radians(th)) * L; hy = by - math.sin(math.radians(th)) * L
            # neck + head
            ink(ctx, [(bx, by), (lerp(bx, hx, .75), lerp(by, hy, .75))], 15, RED_D, 1, seed=730 + i, sketch=False, amp=.4)
            ctx.save(); ctx.translate(hx, hy); ctx.rotate(math.atan2(hy - by, hx - bx))
            pts = ellipse_pts(0, 0, 44, 27, 30)
            ctx.restore()
            ang = math.atan2(hy - by, hx - bx)
            hp = [(hx + x * math.cos(ang) - y * math.sin(ang), hy + x * math.sin(ang) + y * math.cos(ang)) for x, y in pts]
            paper_shape(ctx, hp, mix(RED, RED_D, .2) if not att else RED, 1, seed=740 + i, shadow=.2, grain=.9, outline=INK, ow=1.4)
            if att: glow(ctx, hx, hy - 10, 50, OCHRE_L, .5)
            # ATP / ADP+P tokens on the head
            if u >= 0 or t > c("atp") - 3:
                tok = None
                if u >= .45 and u < .58:
                    fly = ease((u - .45) / .13)
                    tx, ty = lerp(hx + 60, hx, fly), lerp(hy + 170, hy + 4, fly)
                    tok = ('ATP', tx, ty, OCHRE)
                elif u >= .58 or u < 0:
                    tok = ('ADP+P', hx, hy + 4, OCHRE_L)
                elif u < .15:
                    tok = ('ADP+P', hx, hy + 4, OCHRE_L)
                elif u < .45:
                    q = (u - .15) / .3
                    tok = ('ADP', hx, hy + 4, OCHRE_L) if q < .85 else None
                    px, py = hx + 50 + q * 120, hy + 40 + q * 90
                    blob(ctx, px, py, 16, OCHRE_L, 1 - q, seed=750 + i, shadow=.1)
                    text(ctx, "P", px, py + 7, 'sans_b', 20, INK, 1 - q, 'center')
                if tok and ph(t, c("atp") - 2.5, .5) > 0:
                    ta = ph(t, c("atp") - 2.5, .5)
                    s, tx, ty, col = tok
                    rr = 26 if s == 'ATP' else 30
                    blob(ctx, tx, ty, rr, col, ta, seed=760 + i, shadow=.15, outline=hexc('9A6420'), ow=1.2)
                    text(ctx, s, tx, ty + 7, 'sans_b', 18 if len(s) > 3 else 20, INK, ta, 'center')
        # labels
        label(ctx, "actin", 1760, 250, 1700, yA - 16, t, c("uncovers") - .8, font='serif_i', size=44, c=hexc('9A6420'), seed=11)
        label(ctx, "binding sites", 520, 210, 480, yA - 22, t, c("binding") - .1, size=40, c=TEAL, seed=12)
        label(ctx, "myosin heads", 1400, 900, 1250 + 20, yM - 60, t, c("myosin") - .2, font='serif_i', size=44, c=RED_D, seed=13)
        # step captions
        steps = [("latch on", c("latch")), ("pivot & pull", c("pivot")), ("let go", c("let")), ("grab again", c("grab"))]
        for i, (s, t0) in enumerate(steps):
            a = ph(t, t0 - .2, .5) * (1 - ph(t, c("each") - .3, .6))
            if a <= 0: continue
            x = 250 + i * 390
            text(ctx, "%d" % (i + 1), x, 1010, 'title', 44, RED, a, 'center')
            text(ctx, s, x + 30, 1008, 'hand', 40, INK, a, 'left', reveal=ph(t, t0 - .1, .6))
        aa = ph(t, c("atp") - .4, .6)
        if aa > 0:
            caption_card(ctx, "ATP: the energy for every stroke", 960, 1010, t, c("atp") - .4, size=44, seed=790)
        # direction of slide
        sa = win(t, c("pull") - .3, c("millions") - .5)
        if sa > 0:
            arrow(ctx, [(1200, 150), (820, 150)], 3.2, INK, sa, prog=ph(t, c("pull") - .3, .6), seed=795)
            text(ctx, "actin is pulled", 1010, 120, 'hand', 38, INK, sa, 'center')

    # -------------------------------------------------- sarcomere contracting
    def sarc(self, ctx, t, only=False):
        c = self.cue
        con = ph(t, c("filaments") - .2, 2.2, ease)
        z = keys(t, [(0, 1.0), (c("sarcomeres") - .3, 1.0), (c("sarcomeres") + 1.2, .42)])
        ctx.save(); camera(ctx, 960, 540, z)
        per = 1000 * (1 - .22 * con) + 40
        def sfn(i, s, r):
            q = (t * 1.3 + i * .37 + r * .61 + s * .2) % 1.0
            return ease(q / .4) if q < .4 else 1 - ease((q - .4) / .6)
        for j in range(-3, 4):
            if j != 0 and z > .99: continue
            sarcomere(ctx, 960 + j * per, 540, t, con, 1.0, 1.0, stroke_fn=sfn, sites=0, blocked=0, seed=800 + j * 37, rows=2)
        ctx.restore()
        a = win(t, c("filaments") - .3, c("sarcomeres") - .2, .4, .4)
        if a > 0:
            for sgn in (-1, 1):
                x = 960 + sgn * 470
                arrow(ctx, [(x, 180), (x - sgn * 140, 180)], 3.4, RED, a, prog=ph(t, c("filaments") - .2, .6), seed=810 + sgn)
            text(ctx, "filaments slide past each other", 960, 130, 'hand', 48, RED, a, 'center', reveal=ph(t, c("slide") - .3, .8))
        b = ph(t, c("sarcomeres") + .3, .6)
        if b > 0:
            text(ctx, "every sarcomere shortens", 960, 150, 'hand', 50, RED, b, 'center', reveal=b)

    def arm(self, ctx, t):
        c = self.cue
        f = Figure(700, 470, .86)
        th = lerp(.3, 2.0, ph(t, c("whole") - .5, 1.3, ease))
        f.draw(ctx, t, theta=th, skin=0.0, body_a=1.0, glow_biceps=.7, dumbbell=1.0)
        text(ctx, "the whole muscle contracts", 1180, 420, 'serif_i', 58, INK, 1, 'left', reveal=ph(t, c("whole") - .5, .7))
