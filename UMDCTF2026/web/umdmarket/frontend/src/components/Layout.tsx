import { Outlet, Link, useLocation } from "react-router-dom";
import { useApp } from "../lib/store.tsx";
import { balanceToDollars } from "../lib/protocol.ts";

const NEWS_ITEMS = [
  "PayPal acquires Stripe in reverse-merger",
  "Linus Torvalds to rewrite entire kernel in C++ to improve memory safety",
  "Tung Tung Sahur crowned winner of UMDCTF 2025 over Lirili Larila and Tralalero Tralala",
  "Jane Street to consult Claude Mythos on all trades",
  "Cluely pivots entirely to social media marketing as a service",
  "Databricks pioneers new \"1-week vesting schedule\"",
  "Bilewater disqualifies Silksong from GOTY nomination",
  "Curtis Sliwa shot dead by the Gottis and Gambinos",
  "Seattle 2 Line extension closes down after nobody wants to visit Bellevue",
  "Local transgender man applies for wrong HRT, gets $800k annual performance bonus",
  "Rust to allow generic function calls without turbofish: foo<T>()",
  "Return of Jesus Christ market remains close to risk-free rate, but it's probably just a coincidence",
  "Boston redesigns entire city, inspired by its charming Seaport District",
  "Man aims to create a tradeable asset out of any difference in opinion, yet nobody seems to care",
  "Amazon removes free bananas for corporate employees",
  "Meta replaces Horizon Worlds with VRChat",
  "First non-tech billboard spotted in San Francisco",
  "Diavolo becomes #1 prediction market trader with the help of Epitaph",
  "CEOs of Oracle, OpenAI, Anthropic, and Google come together to say that there is no AI bubble",
  "Prediction market trading volume to exceed NYSE",
  "My friend has been trying to arbitrage prediction markets for months, but is stuck on syntax errors",
  "Greeks take back Constantinople",
  "CTF Participant wastes time looking at headlines for a hint",
  "Pinnochio says that Dave's Hot Chicken is mid, nose does not grow",
  "Liking cats linked to being based",
  "Yi Long Ma joins CCP to improve government efficiency",
  "New Klarna API lets users bet on whether customers will repay their DoorDash loans on time",
  "Mathematics PhD student's thesis answers centuries-old unasked question",
  "Kash Patel expresses interest in OpenJDK's Project Valhalla",
  "Market not only remains irrational longer than you can remain solvent, but also transcendental",
  "CTF challenge writer spends longer writing news ticker items than the actual challenge",
  "$NVDA stock price soars after NVIDIA announces $200B investment into NVIDIA",
  "Blind user forgets to write TC at end of post",
  "Clavicular framemogs ASU frat leader in act of revenge",
  "Claude Code just asked you to approve a command",
  "Author gives this challenge's flag to CTF participant, argues insider trading helps price discovery",
  "Bitcoin inventor unmasked: 'and I would've gotten away with it too, if it weren't for you meddling kids!'",
  "MSVC implements all instances of undefined behavior with crypto miner",
  "Seattle to introduce a 9.9% income tax on all income below $1 million",
  "YouTube lecturer criticized for insisting to be called \"Mr.\" while secretly being a professor",
  "All major LLM models fail Humanity's Last Exam after forgetting about the back page",
  "ROBLOX introduces prediction markets for new steal-a-brainrot releases",
  "Anthropic announces ai-powered alternative to the company that just criticized them",
  "Samsung to introduce whatever regression Apple made 5 years ago",
  "CTF challenge writer uses niche technologies instead of making good challenges",
  "Supreme Court rules 5-4 that it is OK for them to be politically motivated",
  "Windows user satisfaction rises 40% after Copilot's rewritten Rust subsystem breaks down",
  "Meta allows users to buy their own data at market rate",
  "Citadel internship application to add Common App essay field under the SAT score field",
  "IBM unveils new quantum computer that factors 15 faster than any classical computer",
  "GPT outage brings down 85% of YC startups for an entire day",
  "Palantir partners with US government to build world's most moral mass surveillance system",
  "Your Rust code just finished compiling in --release",
  "Cryptocurrency enthusiasts eager to take over datacenters if AI doesn't work out",
  "PL researchers discover no real-world use cases for functional programming",
  "New Jersey annexes Staten Island",
  "Amazon's restriction on warehouse bathroom breaks lets them pay $30k to interns to build internal dashboards",
  "Spain blockades the Strait of Gibraltar in an effort to reclaim Gibraltar itself",
  "DeepSeek announces new model rivaling Claude Mythos, set to release 3 weeks after Mythos",
  "Offshore workers protest as their jobs are being replaced by AI",
  "Diamondback endorses UMDMarket as its official prediction market partner",
  "Walmart offers payment via $VOO in light of complaints about inflation",
  "IMC to colocate servers with Truth Social to minimize latency",
];

export function Layout() {
  const { username, balance, logout } = useApp();
  const location = useLocation();
  const isHome = location.pathname === "/";
  const isPortfolio = location.pathname === "/portfolio";
  const isDocs = location.pathname === "/docs";

  return (
    <div className="min-h-screen flex flex-col">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-border bg-[#08080a]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left: Logo + nav */}
            <div className="flex items-center gap-8">
              <Link to="/" className="flex items-center gap-2.5 group">
                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center group-hover:shadow-lg group-hover:shadow-primary/20 transition-shadow">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                    <polyline points="16 7 22 7 22 13" />
                  </svg>
                </div>
                <span className="text-lg font-bold tracking-tight text-white">
                  UMDMarket
                </span>
              </Link>

              <div className="hidden sm:flex items-center gap-1">
                <Link
                  to="/"
                  className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                    isHome
                      ? "bg-surface-3 text-white"
                      : "text-muted hover:text-white hover:bg-surface-2"
                  }`}
                >
                  Markets
                </Link>
                <Link
                  to="/portfolio"
                  className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                    isPortfolio
                      ? "bg-surface-3 text-white"
                      : "text-muted hover:text-white hover:bg-surface-2"
                  }`}
                >
                  Portfolio
                </Link>
                <Link
                  to="/docs"
                  className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                    isDocs
                      ? "bg-surface-3 text-white"
                      : "text-muted hover:text-white hover:bg-surface-2"
                  }`}
                >
                  API Docs
                </Link>
              </div>
            </div>

            {/* Right: Balance + user */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3 px-4 py-2 bg-surface-2 border border-border rounded-xl">
                <div className="text-right">
                  <div className="text-xs text-muted leading-none mb-0.5">
                    Balance
                  </div>
                  <div className="text-sm font-mono font-bold text-yes leading-none">
                    ${balanceToDollars(balance)}
                  </div>
                </div>
                <div className="w-px h-8 bg-border" />
                <div className="text-right">
                  <div className="text-xs text-muted leading-none mb-0.5">
                    {username}
                  </div>
                  <button
                    onClick={logout}
                    className="text-xs text-no/70 hover:text-no font-medium transition-colors leading-none"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Breaking news ticker */}
      <NewsTicker />

      {/* Content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}

function NewsTicker() {
  // Duplicate the items so the scroll loops seamlessly
  const items = [...NEWS_ITEMS, ...NEWS_ITEMS];
  const separator = (
    <span className="mx-6 text-red-300/50 font-black select-none" aria-hidden>
      ///
    </span>
  );

  return (
    <div className="relative bg-red-700 overflow-hidden whitespace-nowrap select-none">
      {/* BREAKING label */}
      <div className="absolute left-0 top-0 bottom-0 z-10 flex items-center px-3 bg-red-900 border-r border-red-600">
        <span className="text-[11px] font-black uppercase tracking-widest text-white">
          Breaking
        </span>
      </div>

      {/* Scrolling text */}
      <div className="ticker-scroll py-2 pl-28">
        {items.map((item, i) => (
          <span key={i} className="inline">
            <span className="text-[12px] font-semibold text-white/95">
              {item}
            </span>
            {separator}
          </span>
        ))}
      </div>
    </div>
  );
}
