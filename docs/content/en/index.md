---
title: Introduction
description: 'Overview of combination shape key addon for Blender'
category: Getting Started
position: 1
fullscreen: false
---

# Combination Shape Keys

A combination shape key is a shape key that is driven by one or more other shape keys. They enable
you to have more precise control over the way in which shape keys deform the model and are
particularly useful in facial animation.

For example, let's say you've set up some shape keys for your character's facial expressions. One
of these shape keys is *satisfaction*, and another *acceptance*.

![Satisfaction Expression Shape Key](media/satisfaction.gif)

![Acceptance Expression Shape Key](media/acceptance.gif)

You're happy with these shape keys in isolation, but when they are used together the combined
deformation is not so great. In this case the effect is a little too much.

![Satisfaction and Acceptance Expression Shape Keys](media/satisfaction_acceptance.gif)

In this case you can create a new combination shape key that corrects the expression when
*satisfaction* and *acceptance* shape keys are used together.

![Satisfaction and Acceptance Expression Combination Shape Key](media/satisfaction_acceptance_combination.gif)

Combination shape keys have been available in other software packages for some time and are
essential to many workflows. This addon brings simple but highly configurable combination shape
keys them to Blender, and does so by building on Blender's native capabilities so that you are
free to share and sell your creations with other users without them needing the addon installed.

It is possible to create and set up combination shape keys in Blender without this addon. In fact
this addon relies mostly on Blender's native drivers to work. Nevertheless, setting things up
manually is time-consuming if you are familiar with how combination shape keys work, and confusing
if you aren't. This addon makes combination shape keys simple and quick to set up, manage and adjust
so you can concentrate on the creative process.
