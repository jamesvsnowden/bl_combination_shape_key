# User-Guide

## Creating New Combination Shape Keys

Once you have installed the addon, You will have some additional options in the
**Shape Key Specials** menu. To create a new combination shape key, select
**New Combination Shape Key** from the specials menu.

Selecting this option will show a panel with a list of available shape keys. Select each shape key
that you want to use a *driver* for the new combination shape key. Once you're happy with your
selection you can go ahead an click **OK**.

The new combination shape key will be created and the selected shape keys will be added as drivers.
You will find the settings for the combination shape key in the **Combination Shape Key Drivers**
panel that will be shown below the other settings in the **Shape Keys** panel.

## Using An Existing Shape Key

If you have already created a shape key that you want to use as a combination shape key, you can
select the **Select Combination Shape Key Drivers** option from the **Shape Key Specials** menu.
Much like the process for creating new combination shape keys, a popup panel will allow you to
select which shape keys you want to use as *drivers*.

## Removing Combination Shape Keys

If you no longer want to use a combination shape key, you can select the
**Remove Combination Shape Key Drivers** from the **Shape Key Specials** menu. This will remove
the driver and clean up the addon's internal data. It will not delete the actual shape key itself
so if you not longer want it you should delete it after this step.

!!!Warning
If you delete the shape key without first removing the combination shape key drivers, you will be
left with an invalid driver and stale data managed by the addon. In practice this should not cause
any issues but in the interest of keeping things clean you should remove the drivers before deleting
the key. Similarly it is advisable not to delete the driver directly yourself.

## The Combination Shape Key Driver List

At the top of the **Combination Shape Key Drivers** panel is the list of the shape keys that are
driving the combination shape key. You can add or remove *drivers* at any time and organize the
list as you see fit. To order of the shape keys in the list does not have an effect on the
functionality of the combination shape key.

## Mode

The **Mode** setting allows you to choose how the shape key values are combined when driving the
combination shape key. The available options are:

<dl>
<dt><strong>Multiply</strong></dt>
<dd>The shape key values are multiplied to produce the combination shape key value (default)</dd>
<dt><strong>Lowest</strong></dt>
<dd>The lowest of the shape key values is used as the value of the combination shape key</dd>
<dt><strong>Highest</strong></dt>
<dd>The highest of the shape key values is used as the value of the combination shape key</dd>
<dt><strong>Average</strong></dt>
<dd>The average (mean) of the shape key values is used to produce the combination shape key value</dd>
</dl>

## Enable Driver

Below the **Mode** setting is a checkbox marked **Enable Driver**. By default it is checked and the
combination shape key driver is active. Unchecking **Enable Driver** will mute the driver being used
to control the combination shape key, doing so means that you can shift the combination shape key's
value in the user interface which can be useful when previewing it's effect. Don't forget to re-enable
it once you're done!

!!!Note
Blender will show an unobtrusive warning about editing driven values. You can safely ignore it.

## Goal

The **Goal** is what you want the combination shape key's value to be when it is fully activated by
the drivers. If you for example have two drivers for the combination shape key and each ahs a value
of 1.0, but the **Goal** is set to 0.8. then the combination shape key's value will be 0.8, not 1.0.

!!!Note
Like shape key values, the goal is not required to be in the 0-1 range, it can be anything up to 10.
However, the shape key's value will still be limited according to the **Range Min/Max** setting for
the shape key in the **Shape Keys** panel.

## Radius

The **Radius** controls how far from the combination shape key's goal it should be before it starts to
be activated. Essentially it adjusts how *soon* the combination shape key begins to affect the
mesh. The lower the **Radius**, the later the combination shape key appears. This can be very useful
when you want to very precisely correct deformation only when other shape keys are fully applied.

## Clamp Value

Depending on the driver values, **Mode** and value ranges used, it is possible that the value of the
combination shape key goes beyond it's **Goal**. If the **Clamp Value** checkbox is checked, the
combination shape key's value will be clamped to the **Goal** value and not driven beyond it.

## Easing

The **Easing** curve allows very fine control over the how the combination shape key is
interpolated into the mesh. You can select from a number of presets using the drop down menus
above the curve display, or select the **Curve** option from the dropdown menu to edit the curve
yourself.
