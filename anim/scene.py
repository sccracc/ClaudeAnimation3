"""Scene base class + shared scene furniture (chapter tags, camera, captions)."""
import json, os
from .core import *

TIMING = json.load(open(os.path.join(ROOT, "script", "timing.json")))
LEAD = 0.55   # seconds of scene before the narration starts
TAIL = 0.75   # after the narration ends

class Scene:
    sid = None
    chapter = None
    extra = 0.0   # extra seconds appended after narration
    lead = LEAD

    def __init__(self):
        if self.sid:
            tm = TIMING[self.sid]
            self.vo = tm["dur"]; self.words = tm["words"]
        else:
            self.vo = 0; self.words = []
        self.dur = self.lead + self.vo + TAIL + self.extra

    def cue(self, word, n=1, off=0.0):
        """local time at which the n-th occurrence of `word` (prefix) starts"""
        k = 0
        for w, a, b in self.words:
            if (w.startswith(word[:-1].lower()) if word.endswith('*') else w == word.lower()):
                k += 1
                if k == n: return self.lead + a + off
        raise KeyError("%s: cue %r #%d not found" % (self.sid, word, n))

    def cue_end(self, word, n=1):
        k = 0
        for w, a, b in self.words:
            if (w.startswith(word[:-1].lower()) if word.endswith('*') else w == word.lower()):
                k += 1
                if k == n: return self.lead + b
        raise KeyError(word)

    def draw(self, ctx, t):
        raise NotImplementedError

def camera(ctx, cx, cy, z=1.0, rot=0.0):
    ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.rotate(rot); ctx.translate(-cx, -cy)

def background(ctx, t, drift=(0, 0)):
    """paper with a gentle parallax drift"""
    paper_bg(ctx, math.sin(t * .05) * 20 + drift[0], math.cos(t * .04) * 12 + drift[1])

def chapter_tag(ctx, t, num, title, t0=0.25, t1=4.2):
    a = win(t, t0, t1, .6, .8)
    if a <= 0: return
    x, y = 90, 96
    p = ph(t, t0, .9, ease)
    # small cut-paper tab
    paper_shape(ctx, rrect_pts(x - 26, y - 44, 70 + text_w(ctx, title, 'serif_i', 38) + 70 * p * 0, 64, 6), CREAM, a * .92, seed=900 + num, shadow=.12, grain=.7)
    text(ctx, "%02d" % num, x - 8, y, 'title', 34, RED, a)
    ink(ctx, [(x + 38, y - 30), (x + 38, y + 6)], 1.5, INK_SOFT, a * .6, seed=901)
    text(ctx, title, x + 52, y - 2, 'serif_i', 38, INK, a, reveal=clamp(p * 1.3))

def caption_card(ctx, s, x, y, t, t0, t1=1e9, size=44, font='serif_i', c=INK, bg=CREAM, align='center', seed=0, pad=26):
    """a paper slip with a line of text"""
    a = win(t, t0, t1, .5, .5)
    if a <= 0: return
    w = text_w(ctx, s, font, size)
    x0 = x - w / 2 if align == 'center' else x if align == 'left' else x - w
    rise = (1 - ph(t, t0, .6, eout)) * 18
    paper_shape(ctx, rect_pts(x0 - pad, y - size * .95 - pad * .55 + rise, w + 2 * pad, size * 1.3 + pad * 1.1), bg, a, seed=seed, shadow=.16, grain=.7)
    text(ctx, s, x0 + w / 2, y + rise, font, size, c, a, 'center', reveal=clamp(ph(t, t0 + .05, .6, ease)))

def zoom_through(ctx, t, t0, dur, focus, draw_prev, draw_next, zmax=6.0, bg_t=0.0):
    """textured loupe zoom: prev zooms into `focus` while next grows out of a paper-rimmed circle"""
    p = clamp((t - t0) / dur)
    if p <= 0:
        draw_prev(ctx); return
    if p >= 1:
        draw_next(ctx); return
    pe = ease(p)
    fx, fy = focus
    C = (lerp(fx, W / 2, pe), lerp(fy, H / 2, pe))
    z = zmax ** pe
    ctx.save(); ctx.translate(*C); ctx.scale(z, z); ctx.translate(-fx, -fy); draw_prev(ctx); ctx.restore()
    r = lerp(20, 1300, pe ** 1.35)
    circ = ellipse_pts(C[0], C[1], r, r, 120)
    circ = jitter(circ, 2.0, .01, 777, True, step=12)
    # shadow ring
    ctx.save(); path(ctx, circ, True); ctx.set_line_width(26); ctx.set_source_rgba(.15, .1, .08, .12); ctx.stroke(); ctx.restore()
    ctx.save(); path(ctx, circ, True); ctx.clip()
    background(ctx, bg_t)
    s = lerp(.25, 1.0, pe)
    ctx.save(); ctx.translate(*C); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2); draw_next(ctx); ctx.restore()
    ctx.restore()
    ink(ctx, circ, 7, CREAM, .95, seed=778, closed=True, sketch=False, amp=.5)
    ink(ctx, circ, 1.4, INK_SOFT, .5, seed=779, closed=True, amp=.8)

def zoom_out(ctx, t, t0, dur, focus, draw_prev, draw_next, zmax=5.0, bg_t=0.0, r_end=0):
    """reverse loupe: prev (a detail) shrinks into `focus` inside a circle while next zooms out to full frame"""
    p = clamp((t - t0) / dur)
    if p <= 0:
        draw_prev(ctx); return
    if p >= 1 and r_end <= 0:
        draw_next(ctx); return
    pe = ease(p)
    fx, fy = focus
    z = zmax ** (1 - pe)
    C = (lerp(W / 2, fx, pe), lerp(H / 2, fy, pe))
    ctx.save(); ctx.translate(*C); ctx.scale(z, z); ctx.translate(-fx, -fy); draw_next(ctx); ctx.restore()
    r = lerp(1300, max(r_end, 10), pe ** .8)
    if r_end <= 0 and p > .92: return
    circ = jitter(ellipse_pts(C[0], C[1], r, r, 120), 2.0, .01, 777, True, step=12)
    a = 1.0 if r_end > 0 else 1 - ph(p, .75, .2)
    ctx.save(); path(ctx, circ, True); ctx.set_line_width(26); ctx.set_source_rgba(.15, .1, .08, .12 * a); ctx.stroke(); ctx.restore()
    ctx.save(); path(ctx, circ, True); ctx.clip()
    ctx.push_group()
    background(ctx, bg_t)
    s = lerp(1.0, (r_end or 120) / 700, pe)
    ctx.save(); ctx.translate(*C); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2); draw_prev(ctx); ctx.restore()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()
    ink(ctx, circ, 7, CREAM, .95 * a, seed=778, closed=True, sketch=False, amp=.5)
    ink(ctx, circ, 1.4, INK_SOFT, .5 * a, seed=779, closed=True, amp=.8)
