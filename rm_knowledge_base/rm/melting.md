# RM's melting

How RM corrects what a melt returns, keeps what is under a tenth, and shows a smelter's part bars. DF's side is in df/melting.md.

## Every melt is measured

- **Status:** decided (2026-10-04) and measured in play
- A melt returns nine tenths of what is in what it melted (refinish-melt.lua, THE MEASURE):
  - **RM's dust and scrap** hold their volume, a sixth and a quarter of a bar.
  - **Anything else** holds the smaller of what it cost to make (df/melting.md) and its own volume. A forge job's loss is the bars' volume in less the item's volume out, paid back as dust and scrap (refinish-job-byproducts.lua), so what stays in an item is the smaller of the two.
  - **A type with no cost known** is credited nine tenths of the lesser of its volume and DF's credit, said once per type.
- **Why nine tenths:** every process loses material. Forging pays its loss back as dust and scrap, so a product and all its waste, brought back to a smelter, still hold what went in; the melt is where the loss is taken. Nine tenths is DF's own yield for items its whole-bar rounding does not distort.
- **DF's credit is not a measure.** It is read only to undo what DF did. From 2026-10-04 until later that day it also capped a melt, which left a melted gold table at DF's one bar of its three; with the cap gone, the table returns 2.7.
- **Before this:** on 2026-10-03 a hijack topped melts up from other stacks and trimmed what was left over. Once DF's own store was found (df/melting.md), the vanilla melt job does the work and RM corrects its credit afterwards.
- **Evidence:** MELT lines in play. Four single scraps make nine tenths of a bar, each kept to the remainder. The gold table was credited 1620, ninety per cent of 1800, and RM made one bar past DF's one.

## Nothing is rounded away

- **Status:** decided (2026-10-04) and measured
- DF's store holds whole tenths. The part of a melt under a tenth (a scrap is 2.5 tenths, a coin a fiftieth of one) is the smelter's REMAINDER for that metal, kept in RM's own bank (refinish-persist-banks, REFINISH_MELT) by metal name, and added in at that smelter's next melt of the metal. A remainder whose smelter is gone is dropped at the next start, as DF drops its own part bars with a smelter.
- **Before this:** the credit was rounded down, and four single scraps made 0.8 of a bar.

## A melt pays no byproducts

- **Status:** decided (2026-10-04)
- Melting turns metal into metal, so melt jobs are not covered by the byproduct service. Counted from the items a melt held, the old coverage also overpaid, because what DF keeps in its store is not an item.

## A smelter's store always covers the array

- **Status:** code (2026-10-04)
- DF writes a melted metal's entry by its index, and a store sized before a finish was minted ends before that finish (df/melting.md). Before any melt at a smelter, the melt service grows that smelter's store to the array. At every load the ledger fits every furnace's store to the array (rm/save-system.md).

## The melt bank shows on the building sheet

- **Status:** decided and measured in play (2026-10-04)
- RM's bank readout (refinish-bank-readout.lua) is a panel beside the building sheet whose rows come from PROVIDERS registered in `_G.refinish_bank_providers`; the panel itself moved out of Making Fuel, which now hands it its fuel rows. The melt service provides a smelter's "melt bank": one row per metal with a part bar waiting, store and remainder together, or "empty".
- A section after the first draws its own title as a heading, so a smelter with Making Fuel reads "furnace bank" over the fuel rows and "melt bank" over its part bars.
- The flash is kept per building. Keyed by currency alone, as the fuel panel had it, opening one furnace after another flashed every row whose bank differed between them (found in a mock).
