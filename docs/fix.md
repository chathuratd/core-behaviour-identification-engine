First: what your input REALLY is (and you’re underestimating it)

Your input is not user text.
Your input is:

A semi-structured behavioral assertion produced by an upstream system.

That means:

It already encodes intent

It already made decisions

It already threw information away

So if you embed it like raw language, you’re double-diluting semantics.

That’s why things feel mushy.

What the upstream system actually gives you (implicitly)

Even if it outputs “behavior text”, it already contains structure like:

canonical action verbs

normalized entities

outcome signals

system/user perspective

You’re wasting that by flattening everything into one sentence → one embedding.

That’s your first blind spot.

Revised solution (WITH your constraint respected)
LAYER 1 — Treat extracted behavior as a typed object, not text

Each behavior should be a record, even if fields are partially empty:

Behavior {
  actor_type
  action
  object
  outcome
  qualifiers
  raw_behavior_text   // optional
}


If you already receive this implicitly, make it explicit.

If you don’t do this, your system is intellectually dishonest — you’re pretending structure doesn’t exist when it does.

LAYER 2 — Stop single-embedding stupidity

This is where you’re still wrong today.

Do NOT embed the whole behavior as one string.

Instead:

Embed action + object

Encode outcome categorically

Encode actor_type categorically

Optionally embed qualifiers

Then combine distances after, not before.

Why?
Because:

Action similarity ≠ outcome similarity

Same action + different outcome is NOT same behavior

Your current system can’t enforce this distinction.

LAYER 3 — Distance is multi-channel, not cosine-only

Right now you’re doing:

cosine( full_embedding )

That’s lazy and wrong for your data.

You need:

D = w1 * cosine(action_object_embedding)
  + w2 * categorical_distance(outcome)
  + w3 * categorical_distance(actor)
  + w4 * qualifier_distance


Now density actually means something.

Without this, HDBSCAN is clustering linguistic accidents.

LAYER 4 — HDBSCAN becomes legitimate (finally)

With structured distance:

Density corresponds to behavioral sameness

Noise actually means “not core”

Cluster stability increases dramatically

So no — HDBSCAN was not the villain.
Your distance space was garbage.

LAYER 5 — Core behavior ≠ frequent behavior

This is another assumption you’re quietly making.

A behavior is core if:

It appears across contexts

It survives representation perturbation

It has high structural agreement

It’s semantically tight

Frequency alone is a weak signal.

Your system currently worships frequency.

What you should NOT do (and I’m calling this out clearly)

❌ Do NOT retrain embeddings
❌ Do NOT throw more data at HDBSCAN
❌ Do NOT add “LLM naming” and pretend it’s intelligence

All of those are cosmetics over a cracked foundation.

What changes in your presentation narrative

You should say:

“Our system does behavior consolidation, not behavior extraction.
We operate on normalized behavioral assertions, and identify stable behavioral patterns using multi-channel similarity and density analysis.”

That’s honest. That’s defensible.

Right now, if someone smart listens closely, they’ll realize you’re clustering sentences.

The hard truth

Your upstream extractor already did the hard semantic work.

Your mistake was:

throwing that structure away and hoping embeddings recover it.

They won’t.