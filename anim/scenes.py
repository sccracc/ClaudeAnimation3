"""All scenes of the film, in order."""
from .core import *
from .scene import *
from .figure import Figure
from .assets import *

# ============================================================== 01 HOOK
class Hook(Scene):
    sid = "s01_hook"
    lead = 1.3

    def sfx(self):
        return [(self.cue("so") + .2, 'zoom')]

    def draw(self, ctx, t):
        c_heavy = self.cue("heavy"); c_signal = self.cue("signal"); c_pull = self.cue("pull")
        c_do = self.cue("do"); c_body = self.cue("body"); c_but = self.cue("but"); c_after = self.cue("after")
        c_so = self.cue("so", 1)
        background(ctx, t)
        # camera: settle, then drift aside for the during/after cards, then push into the arm
        push = ph(t, c_so + .2, 2.4, ein)
        f = Figure(760, 470, 0.86)
        cam = keys(t, [(0, (800, 560, 1.18)), (c_pull, (790, 560, 1.18)), (c_do + .3, (960, 540, 1.0)), (c_but - .3, (960, 540, 1.0)), (c_but + .7, (1180, 540, 1.0))])
        cx, cy, z = cam
        zx, zy = f.P((40, 150))
        cx = lerp(cx, zx, ease(push)); cy = lerp(cy, zy, ease(push))
        z = lerp(z, 5.5, push)
        ctx.save(); camera(ctx, cx, cy, z)
        # arm motion
        reps = 0.0
        th = 0.15
        curl1 = ph(t, c_heavy - .2, 1.3, ease)
        th = lerp(0.15, 1.95, curl1)
        if t > c_do - .4:  # repeated reps
            k = (t - (c_do - .4)) / 1.25
            th = 1.95 - (1.8 * (0.5 - 0.5 * math.cos(min(k, 4.0) * 2 * math.pi))) if k < 4.0 else 1.95
            reps = min(k, 4.0)
        grow = ph(t, c_body, 2.2, ease) * .5
        # entrance
        ent = ph(t, 0.0, 1.1, eout)
        ctx.save(); ctx.translate(0, (1 - ent) * 40)
        peel_r = 150 * ph(t, c_pull - .9, 1.0, eback)
        peel = (f.P((40, 120))[0], f.P((40, 120))[1], peel_r) if peel_r > 1 else None
        brain = ph(t, c_signal - .5, .7)
        nerve = ph(t, c_signal - .2, .5)
        pulses = []
        for k in range(8):
            st = c_signal + k * 0.35
            if t > st: pulses.append(clamp((t - st) / .8))
        pulses = [p for p in pulses if p < 1]
        f.draw(ctx, t, theta=th, skin=1.0, body_a=ent, brain=brain, nerve=nerve * (1 - ph(t, c_but, .6)), pulse=pulses if t < c_do + 2 else None,
               peel=peel, grow=grow, glow_biceps=.8 * win(t, c_pull - .5, c_do + 1.5) + .6 * win(t, c_body, c_but + .2))
        ctx.restore()
        # annotations (world space)
        bx, by = f.P((-18, -335))
        label(ctx, "brain", bx + 190, by - 70, bx + 40, by - 20, t, c_signal - .3, size=36, a=1 - ph(t, c_do - .3, .5), seed=1)
        mx, my = f.P((60, 120))
        label(ctx, "thousands of muscle cells", mx + 260, my + 40, mx + 70, my + 20, t, c_pull - .2, size=36, a=1 - ph(t, c_do + 1.0, .5), seed=2)
        # rep tally + "stronger" note
        ta = win(t, c_do, c_but + .3, .4, .6)
        if ta > 0:
            tx, ty = 1120, 330
            text(ctx, "rep after rep", tx, ty - 40, 'serif_i', 58, INK_SOFT, ta, reveal=ph(t, c_do, .8))
            tally(ctx, tx, ty, min(14, int(reps * 3.5)), ta, seed=5, h=64, sp=20)
            sa = ph(t, c_body + .6, .8)
            if sa > 0:
                arrow(ctx, [(tx + 20, ty + 230), (tx + 20, ty + 110)], 3, RED, ta, prog=sa, seed=6)
                text(ctx, "rebuilt stronger", tx + 50, ty + 190, 'hand', 56, RED, ta, reveal=ph(t, c_body + .9, .9))
        ctx.restore()
        # during / after cards (screen space)
        ca = win(t, c_but - .1, c_so + 1.2, .6, .6)
        if ca > 0:
            for i, (title, sub, t0) in enumerate([("During", "the workout", c_but + .1), ("After", "the workout", c_after - .2)]):
                x = 1080 + i * 390; y = 330
                p = ph(t, t0, .8, eback)
                if p <= 0: continue
                ctx.save(); ctx.translate(x + 170, y + 190); ctx.rotate((-.03 if i == 0 else .025) * p); ctx.scale(.9 + .1 * p, .9 + .1 * p); ctx.translate(-(x + 170), -(y + 190))
                paper_shape(ctx, rect_pts(x, y, 340, 380), CREAM if i == 0 else hexc('F6E9D2'), ca * clamp(p), seed=300 + i, shadow=.22)
                text(ctx, title, x + 170, y + 80, 'title', 60, INK, ca, 'center')
                text(ctx, sub, x + 170, y + 125, 'serif_i', 34, INK_SOFT, ca, 'center')
                if i == 0:
                    dumbbell_icon(ctx, x + 170, y + 250, .95, ca, seed=310)
                else:
                    moon_icon(ctx, x + 150, y + 255, 62, ca, seed=320)
                ctx.restore()
            # "during" gets de-emphasised, "after" is circled
            dim = ph(t, c_after, .6)
            if dim > 0:
                ink(ctx, [(1105, 690), (1395, 360)], 3, INK_SOFT, ca * dim * .6, prog=dim, seed=330)
            circle_mark(ctx, 1640, 520, 215, 235, t, c_after + .25, RED, 3.6, ca, seed=331)
            text(ctx, "where the change happens", 1640, 820, 'hand', 44, RED, ca, 'center', reveal=ph(t, c_after + .15, .8))
        # fade to paper at the very end of the push (handoff to title)
        if push > .75:
            set_c(ctx, PAPER, ph(t, c_so + 1.8, .6, ease)); ctx.paint()


# ============================================================== TITLE
class Title(Scene):
    extra = 0.0
    def __init__(self):
        super().__init__(); self.dur = 5.4

    def draw(self, ctx, t):
        background(ctx, t)
        # sliding paper strips
        for i, (c, y, h, d) in enumerate([(RED, 318, 26, 0.0), (OCHRE_L, 356, 12, .15), (TEAL_L, 720, 14, .3), (RED_L, 748, 8, .45)]):
            p = ph(t, .1 + d, 1.1, eout)
            x0 = lerp(-900, 0, p) if i % 2 == 0 else lerp(W + 900, 0, p)
            paper_shape(ctx, [(x0 + 250, y), (x0 + 1670, y - 4), (x0 + 1670, y + h), (x0 + 250, y + h + 3)], c, win(t, 0, 5.2, .3, .6), seed=400 + i, shadow=.14, amp=2.2)
        a = 1 - ph(t, 4.6, .7)
        # sarcomere banding motif
        mp = ph(t, .6, 1.8, ease)
        for k in range(24):
            x = 560 + k * 34
            if (k + 1) / 24 > mp + .05: break
            hgt = 34 if k % 6 == 0 else 20 if k % 3 == 0 else 12
            ink(ctx, [(x, 660 - hgt / 2), (x, 660 + hgt / 2)], 2.2 if k % 6 == 0 else 1.4, INK_SOFT, a * .7, seed=410 + k, sketch=False)
        text(ctx, "Under Tension", 960, 560, 'title', 150, INK, a, 'center', reveal=ph(t, .5, 1.4, ease), rise=10)
        text(ctx, "What actually happens to your muscles when you work out", 960, 630, 'serif_i', 46, INK_SOFT, a, 'center', reveal=ph(t, 1.4, 1.5, ease))


from .sc_anatomy import Anatomy
from .sc_contract import Contraction
from .sc_mid import Recruitment, Fatigue, Damage
from .sc_end import Repair, Neural, Recovery, Takeaway, EndCard

def sequence():
    """(scene, transition-into-this-scene)"""
    return [(Hook(), None), (Title(), 'fade'), (Anatomy(), 'right'), (Contraction(), 'right'), (Recruitment(), 'right'), (Fatigue(), 'up'), (Damage(), 'right'), (Repair(), 'right'), (Neural(), 'up'), (Recovery(), 'right'), (Takeaway(), 'right'), (EndCard(), 'fade')]
