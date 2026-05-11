# Saltmere — Hub Zone Design

## Concept
Saltmere is a walled trading town at the mouth of the Pale River. It smells of salt, fish, and coal smoke. It's busy in the day, tense at night. The Adventurers' Guild operates from a reclaimed warehouse by the river gate. The temple of the Unbroken Sun is the tallest building; the Pale Thread has been leaving tokens near its steps, which the priests are trying to ignore.

## Zone Sections

### The River Gate District
*Entry zone. First impression of Saltmere.*
- Guild noticeboard (quest board)
- Ferry across the Pale River (leads to Ashfall Crossing questline)
- River market: vendors, fishers, one merchant who knows more than he sells
- Companion reactions: Brann scans exits automatically; Lyra samples the river water and frowns; Ossian counts the guards

### The Merchant Quarter
*Commerce, information, tension*
- Main market: equipment vendor, herbalist, Fletcher
- The Crow's Rest Tavern: rumours, downtime conversations, possible fights
- Back alley where Ossian's dead drop will eventually appear (Act 2)
- The Assessor's Hall: licenses, contracts, bribes

### The Temple District
*Unbroken Sun worship, growing Pale Thread presence*
- Temple interior: healing vendor, lore fragments, a haunted confession booth
- Memorial stones outside: players can leave offerings (minor trust events)
- Pale Thread token spawns appear here after Act 1 starts

### The Garrison
*Town guard presence*
- Guards who know Brann by reputation (he doesn't know this yet)
- Notice board with bounties: minor side content
- Cells with a prisoner who has information relevant to Act 2

## Companion Hub Behaviour

In Saltmere, companions are in their most natural state — talking, wandering, having opinions.

**Brann:**
- Sits with his back to walls in the tavern
- Asks the guards questions about patrol patterns (habit)
- Will mention the garrison memorial if trust is high ("My father's name was on a wall like that once")

**Lyra:**
- Gravitates to the market's herb vendor and gets into arguments about classification
- Samples everything edible
- Avoids the temple district unless prompted — deflects questions about why

**Ossian:**
- Always knows where the exits are
- Will spend time alone if the party is in the tavern; rejoins without comment
- On one visit, a courier delivers a letter; he reads it and burns it without explaining

## Trust Events in Saltmere
| Action | Event | Delta |
|--------|-------|-------|
| Give coin to beggar at river gate | helped_villager | +2 |
| Haggle aggressively and insult merchant | harmed_villager | -3 |
| Start brawl in the Crow's Rest | harmed_villager | -5 |
| Offer temple donation | complimented_companion (Brann only if he sees) | +2 |
| Leave companion alone for 30+ minutes | dismissed_companion_idea | -2 |
| Invite companion for a drink | confided_in_companion | +3 |
| Back companion in a social conflict | defended_companion | +8 |
