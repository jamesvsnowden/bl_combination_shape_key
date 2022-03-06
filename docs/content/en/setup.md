---
title: Creating Combination Shape Keys
menuTitle: Creating CSKs
description: 'Managing combination shape key addon for Blender'
category: User Guide
position: 4
fullscreen: false
---
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
