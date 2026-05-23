package market

// TickerDef defines a prediction market ticker.
type TickerDef struct {
	ID           uint16
	Name         string
	Description  string
	InitialPrice uint16 // price units: 1 = $0.0001, 10000 = $1.0000
}

// Tickers is the hardcoded list of prediction markets.
var Tickers = []TickerDef{
	{0, "AMTRAK_NEC", "Will an Amtrak NEC train be delayed today?", 8000},
	{1, "P_EQ_NP", "P = NP?", 1500},
	{2, "MRBEAST_SLOP", "Will the next MrBeast video be slop?", 7500},
	{3, "KRUSKAL_RETIRE", "Clyde Kruskal retired by 2030?", 3500},
	{4, "RAIN_SEA", "Will it rain in Seattle in April?", 8500},
	{5, "AI_SWE_REPLACE", "90% of SWE replaced by AI in 6 months?", 1500},
	{6, "CTF_PRIZES", "CTF prizes distributed within 1 month?", 4500},
	{7, "BILLIONAIRE_JAIL", "Will an evil billionaire be arrested by May?", 2000},
	{8, "HL3_2100", "Half-Life 3 before 2100?", 2500},
	{9, "PARTY_WINS", "Will my preferred political party win the election?", 5000},
	{10, "HINT_RELEASE", "Hint released before end of CTF?", 7500},
	{11, "UMD_CS_T10", "UMD Graduate CS Top 10 Ranking for 2026?", 5500},
	{12, "USDT_ABOVE_1", "Will USDT break above $1.00?", 3000},
	{13, "MIDEAST_PEACE", "Will conflict in the Middle East ever end?", 1500},
	{14, "MATH404_A", "MATH404 grade at least an A?", 4000},
}
