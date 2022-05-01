---
title: Removing CSKs
description: 'Removing combination shape keys'
category: User Guide
position: 8
fullscreen: false
---
## Removing Combination Shape Keys

If you no longer want to use a combination shape key, you can select the
**Remove Combination Shape Key Drivers** from the **Shape Key Specials** menu. This will remove
the driver and clean up the addon's internal data. It will not delete the actual shape key itself
so if you not longer want it you should delete it after this step.

<alert type="warning">

If you delete the shape key without first removing the combination shape key drivers, you will be
left with an invalid driver and stale data managed by the addon. In practice this should not cause
any issues but in the interest of keeping things clean you should remove the drivers before deleting
the key. Similarly it is advisable not to delete the driver directly yourself.

</alert>