import { Link } from "react-router-dom";

export function ApiDocsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-10 animate-fade-in">
        <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
          API Documentation
        </h1>
        <p className="text-muted text-sm">
          Binary wire protocol reference for the UMDMarket WebTransport server.
        </p>
        <p className="mt-3 text-xs text-muted">
          Want an LLM-readable version? Click{" "}
          <Link
            to="/docs/llms"
            className="text-primary hover:text-primary-hover underline underline-offset-2"
          >
            here
          </Link>.
        </p>
      </div>

      <div className="space-y-8">
        {/* Overview */}
        <Section title="Overview" delay={1}>
          <P>
            UMDMarket is built for <Hl>high-frequency traders</Hl>: a
            tight binary wire format, signed quote tokens, 100ms tick cadence,
            and a low-latency <Hl>WebTransport (HTTP/3 + QUIC)</Hl> transport,
            engineered so co-located bots can round-trip orders in
            microseconds instead of milliseconds.
          </P>
          <P>
            The server listens on port <Code>4443/udp</Code>. All multi-byte
            integers are <Hl>little-endian</Hl>. There are two transport
            channels:
          </P>
          <ul className="list-disc list-inside text-sm text-text-dim space-y-1 mt-3 ml-2">
            <li>
              <Hl>Datagrams</Hl>: unreliable, server→client only (price
              quotes)
            </li>
            <li>
              <Hl>Bidirectional streams</Hl>: reliable, one request/response
              per stream
            </li>
          </ul>
          <P>
            Connect to <Code>https://HOST:4443/wt</Code> via the WebTransport
            API. The server uses a self-signed certificate generated at image
            build time; its SHA-256 hash is baked into this frontend bundle
            and passed as <Code>serverCertificateHashes</Code> automatically.
          </P>
        </Section>

        {/* Types */}
        <Section title="Wire Types" delay={2}>
          <Table
            headers={["Type", "Size", "Description"]}
            rows={[
              ["uint8", "1 byte", "Unsigned 8-bit integer"],
              ["uint16", "2 bytes", "Little-endian unsigned 16-bit integer"],
              ["uint32", "4 bytes", "Little-endian unsigned 32-bit integer"],
              ["uint64", "8 bytes", "Little-endian unsigned 64-bit integer"],
              [
                "string8",
                "1 + N bytes",
                "[length:uint8] [data:N bytes]: length-prefixed string",
              ],
              [
                "string16",
                "2 + N bytes",
                "[length:uint16] [data:N bytes]: length-prefixed string",
              ],
            ]}
          />
        </Section>

        {/* Pricing */}
        <Section title="Pricing Model" delay={3}>
          <P>
            All prices and balances are <Hl>integers</Hl>. No floating point
            anywhere.
          </P>
          <Table
            headers={["Concept", "Type", "Unit", "Example"]}
            rows={[
              ["Price", "uint16", "1 = $0.0001", "4500 = $0.4500 = 45.00%"],
              [
                "Balance",
                "uint64",
                "1 = $0.0001",
                "1,000,000 = $100.00",
              ],
              [
                "Quantity",
                "uint32",
                "1 contract",
                "100 = 100 contracts",
              ],
              [
                "Cost",
                "uint64",
                "price × qty",
                "4500 × 100 = 450,000 ($45.00)",
              ],
            ]}
          />
          <P>
            YES + NO = <Code>10000</Code> (PriceUnit). A YES price of 7000
            means NO costs 3000. Prices range from <Code>1</Code> ($0.0001) to{" "}
            <Code>9999</Code> ($0.9999).
          </P>
        </Section>

        {/* Constants */}
        <Section title="Server Constants" delay={3}>
          <Table
            headers={["Constant", "Value", "Description"]}
            rows={[
              ["PriceUnit", "10000", "YES + NO = 10000"],
              [
                "MaxAge",
                "5",
                "Max ticks a quote can be old (500ms at 100ms/tick)",
              ],
              [
                "MinCooldown",
                "50",
                "Min ticks between trades (5 seconds)",
              ],
              [
                "MaxStep",
                "±50",
                "Max price movement per tick (±$0.0050)",
              ],
              ["TickInterval", "100ms", "Price update frequency (10 ticks/sec)"],
              [
                "StartingBalance",
                "1,000,000",
                "New account balance ($100.00)",
              ],
              ["FlagPrice", "10,000,000", "Cost to buy the flag ($1,000.00)"],
              [
                "ResendWindow",
                "500",
                "Ticks of RESEND history retained per session (~50s)",
              ],
              [
                "QuoteHmacSize",
                "8 bytes",
                "Truncated HMAC-SHA256 attached to every quote",
              ],
            ]}
          />
        </Section>

        {/* Datagrams */}
        <Section title="Datagrams (Server → Client)" delay={3}>
          <SubSection title="QUOTE (0x01)">
            <P>
              Sent every tick (~100ms) for each subscribed ticker. Unreliable
              delivery. Each quote is signed with an <Hl>HMAC-SHA256</Hl>{" "}
              (truncated to 8 bytes) over the concatenation of{" "}
              <Code>seq || ticker_id || yes_price</Code> using a server-held
              secret. A quote must be echoed back intact (including its HMAC)
              in TRADE requests.
            </P>
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x01" },
                { name: "seq", type: "uint16", desc: "Server sequence number" },
                { name: "ticker_id", type: "uint16", desc: "Ticker identifier" },
                {
                  name: "yes_price",
                  type: "uint16",
                  desc: "YES price at that seq (0–10000)",
                },
                {
                  name: "hmac",
                  type: "8 bytes",
                  desc: "Truncated HMAC-SHA256 over (seq, ticker_id, yes_price)",
                },
              ]}
              total={15}
            />
          </SubSection>

          <SubSection title="RESOLVED (0x02)">
            <P>
              Emitted once when a market resolves. A resolution fires when
              the ticker's price would cross <Code>MinPrice=1</Code>{" "}
              (resolves NO) or <Code>MaxPrice=9999</Code> (resolves YES).
              Any open positions in that ticker are <Hl>wiped</Hl>; the
              ticker's price immediately resets to its initial price and
              trading resumes on the next tick. Clients should drop any
              cached quote token for the resolved ticker since the next
              QUOTE will carry a fresh token against the reset price.
            </P>
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x02" },
                { name: "ticker_id", type: "uint16", desc: "Ticker that just resolved" },
                { name: "outcome", type: "uint8", desc: "0 = YES, 1 = NO" },
              ]}
              total={4}
            />
          </SubSection>
        </Section>

        {/* Bidi streams */}
        <Section title="Bidirectional Streams (Request / Response)" delay={3}>
          <P>
            Each action uses <Hl>one bidi stream</Hl>. The client opens a
            bidirectional stream, writes the request bytes, closes its write
            side, then reads the full response from the server.
          </P>

          <SubSection title="How to serialize a request">
            <P>
              A request is a single byte buffer built by concatenating fields
              in order. The <Hl>first byte</Hl> is always the{" "}
              <Hl>message type</Hl> (e.g. <Code>0x20</Code> for REGISTER,{" "}
              <Code>0x30</Code> for TRADE). The remaining fields follow
              immediately after, in the order listed, with no padding or
              delimiters between them.
            </P>
            <P>
              All multi-byte integers use <Hl>little-endian</Hl> byte order.
              For example, the uint16 value <Code>4443</Code> (0x115B) is
              serialized as the bytes <Code>5B 11</Code>. In JavaScript, use{" "}
              <Code>DataView.setUint16(offset, value, true)</Code> where the
              third argument enables little-endian mode.
            </P>
            <P>
              Strings are length-prefixed: write the length as a uint8 (for
              string8) or uint16 (for string16), then the raw UTF-8 bytes of
              the string. No null terminator.
            </P>
          </SubSection>

          <SubSection title="Example: serializing a SUBSCRIBE request">
            <P>
              SUBSCRIBE (type <Code>0x22</Code>) takes one field:{" "}
              <Code>ticker_id:uint16</Code>. To subscribe to ticker 3:
            </P>
            <div className="mt-3 p-4 bg-surface rounded-xl border border-border font-mono text-sm text-text-dim leading-relaxed">
              <div className="text-muted text-xs uppercase tracking-wider mb-2 font-sans font-medium">
                Byte layout
              </div>
              <div>
                <Code>22</Code>{" "}
                <span className="text-muted mx-1">|</span>{" "}
                <Code>03 00</Code>
              </div>
              <div className="text-xs text-muted mt-2">
                0x22 = SUBSCRIBE type, 0x0003 LE = ticker_id 3
              </div>
              <div className="text-xs text-muted mt-1">
                Total: 3 bytes
              </div>
            </div>
          </SubSection>

          <SubSection title="Response format">
            <P>
              The first byte of every response is a <Hl>status code</Hl>.{" "}
              <Code>0x00</Code> means success, anything else is an error.
            </P>
            <div className="mt-3 p-4 bg-surface rounded-xl border border-border font-mono text-sm text-text-dim">
              <div>
                Success: <Code>[0x00] [payload fields...]</Code>
              </div>
              <div className="mt-1">
                Error:{" "}
                <Code>[status:uint8] [msg_len:uint16] [msg:N bytes]</Code>
              </div>
            </div>
            <P>
              On success, the payload fields follow the status byte in order,
              using the same serialization rules. On error, the status byte is
              followed by a uint16-prefixed error message string.
            </P>
          </SubSection>
        </Section>

        {/* REGISTER */}
        <Section title="REGISTER (0x20)" delay={3}>
          <P>
            Create a new account. Username must be 8+ alphanumeric characters.
            Password must be 12+ characters with uppercase, lowercase, digit,
            and special character.
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x20" },
                { name: "username", type: "string8", desc: "8+ alphanumeric" },
                {
                  name: "password",
                  type: "string8",
                  desc: "12+ chars, mixed requirements",
                },
              ]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                {
                  name: "balance",
                  type: "uint64",
                  desc: "Starting balance (1,000,000)",
                },
              ]}
            />
          </SubSection>
        </Section>

        {/* LOGIN */}
        <Section title="LOGIN (0x21)" delay={3}>
          <P>
            Authenticate with an existing account. Disconnects any prior session
            for this user (one session per user).
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x21" },
                { name: "username", type: "string8" },
                { name: "password", type: "string8" },
              ]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                { name: "balance", type: "uint64", desc: "Current balance" },
              ]}
            />
          </SubSection>
        </Section>

        {/* SUBSCRIBE */}
        <Section title="SUBSCRIBE (0x22)" delay={3}>
          <P>
            Start receiving QUOTE datagrams for a ticker. The server also
            begins retaining this ticker's prices in its per-session RESEND
            window from this point forward.
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x22" },
                { name: "ticker_id", type: "uint16" },
              ]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
              ]}
            />
          </SubSection>
        </Section>

        {/* UNSUBSCRIBE */}
        <Section title="UNSUBSCRIBE (0x23)" delay={3}>
          <P>Stop receiving quotes for a ticker.</P>
          <SubSection title="Request">
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x23" },
                { name: "ticker_id", type: "uint16" },
              ]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
              ]}
            />
          </SubSection>
        </Section>

        {/* FETCH_TICKERS */}
        <Section title="FETCH_TICKERS (0x24)" delay={3}>
          <P>
            Get all market definitions. Does <Hl>not</Hl> include current
            prices; prices come via QUOTE datagrams after subscribing.
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[{ name: "type", type: "uint8", value: "0x24" }]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                { name: "count", type: "uint16", desc: "Number of tickers" },
                {
                  name: "tickers[]",
                  type: "repeated",
                  desc: "For each ticker:",
                },
                { name: "  id", type: "uint16", desc: "Ticker identifier" },
                { name: "  name", type: "string8", desc: 'e.g. "BTC_100K"' },
                {
                  name: "  description",
                  type: "string16",
                  desc: "Market question",
                },
              ]}
            />
          </SubSection>
        </Section>

        {/* FETCH_HISTORY */}
        <Section title="FETCH_HISTORY (0x25)" delay={3}>
          <P>
            Get minute-by-minute historical prices for a ticker. One snapshot
            is recorded every 60 seconds.
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x25" },
                { name: "ticker_id", type: "uint16" },
                {
                  name: "minutes",
                  type: "uint16",
                  desc: "How many minutes of history",
                },
              ]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                { name: "count", type: "uint16", desc: "Number of records" },
                { name: "records[]", type: "repeated", desc: "For each record:" },
                {
                  name: "  timestamp",
                  type: "uint64",
                  desc: "Unix timestamp (seconds)",
                },
                {
                  name: "  yes_price",
                  type: "uint16",
                  desc: "YES price at that time",
                },
              ]}
            />
          </SubSection>
        </Section>

        {/* RESEND */}
        <Section title="RESEND (0x26)" delay={3}>
          <P>
            Ask the server to re-send a previously-emitted quote. Datagrams
            are unreliable and can be dropped in flight; if the client
            notices a gap in the QUOTE stream, it can request the missed
            quote here. The server looks up the price it had at the
            requested <Code>seq</Code> for the requested ticker and returns
            a freshly-signed quote the client can then use in TRADE.
          </P>
          <P>
            The server keeps a <Hl>bounded history window</Hl>{" "}
            (<Code>ResendWindow</Code> ticks). Requests for a seq outside
            the window fail with <Code>ERR_RESEND_UNAVAILABLE</Code>.
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x26" },
                {
                  name: "seq",
                  type: "uint16",
                  desc: "Sequence number of the missed quote",
                },
                { name: "ticker_id", type: "uint16" },
              ]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                {
                  name: "seq",
                  type: "uint16",
                  desc: "Server seq stamped on the returned quote",
                },
                { name: "ticker_id", type: "uint16" },
                {
                  name: "yes_price",
                  type: "uint16",
                  desc: "YES price at the requested seq",
                },
                {
                  name: "hmac",
                  type: "8 bytes",
                  desc: "HMAC over (seq, ticker_id, yes_price)",
                },
              ]}
            />
          </SubSection>
        </Section>

        {/* TRADE */}
        <Section title="TRADE (0x30)" delay={3}>
          <P>
            Execute a trade by <Hl>echoing a signed quote</Hl> back to the
            server. The quote identifies both the ticker and the price you
            want to fill at; its HMAC proves the server issued it. Quotes
            come from either QUOTE datagrams or RESEND responses. The server
            verifies the HMAC, checks the quote is still fresh (within{" "}
            <Code>MaxAge</Code> ticks of the current seq), enforces the
            inter-trade cooldown, and fills at <Code>yes_price</Code> (or
            its complement for NO sides).
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[
                { name: "type", type: "uint8", value: "0x30" },
                {
                  name: "seq",
                  type: "uint16",
                  desc: "From the echoed quote",
                },
                { name: "ticker_id", type: "uint16", desc: "From the echoed quote" },
                {
                  name: "yes_price",
                  type: "uint16",
                  desc: "From the echoed quote",
                },
                {
                  name: "hmac",
                  type: "8 bytes",
                  desc: "From the echoed quote",
                },
                { name: "side", type: "uint8", desc: "Trade direction (see below)" },
                { name: "qty", type: "uint32", desc: "Number of contracts" },
              ]}
            />
          </SubSection>
          <SubSection title="Side Values">
            <Table
              headers={["Value", "Constant", "Description"]}
              rows={[
                ["0x00", "BUY_YES", "Buy YES contracts at yes_price"],
                [
                  "0x01",
                  "BUY_NO",
                  "Buy NO contracts at (10000 − yes_price)",
                ],
                ["0x02", "SELL_YES", "Sell YES contracts at yes_price"],
                [
                  "0x03",
                  "SELL_NO",
                  "Sell NO contracts at (10000 − yes_price)",
                ],
              ]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                {
                  name: "fill_price",
                  type: "uint16",
                  desc: "Actual price filled at",
                },
                {
                  name: "new_balance",
                  type: "uint64",
                  desc: "Updated account balance",
                },
              ]}
            />
          </SubSection>
        </Section>

        {/* PORTFOLIO */}
        <Section title="PORTFOLIO (0x40)" delay={3}>
          <P>Get current balance and all open positions.</P>
          <SubSection title="Request">
            <WireFormat
              fields={[{ name: "type", type: "uint8", value: "0x40" }]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                { name: "balance", type: "uint64", desc: "Current balance" },
                {
                  name: "count",
                  type: "uint16",
                  desc: "Number of positions",
                },
                {
                  name: "positions[]",
                  type: "repeated",
                  desc: "For each position:",
                },
                { name: "  ticker_id", type: "uint16" },
                {
                  name: "  yes_qty",
                  type: "uint32",
                  desc: "YES contracts held",
                },
                {
                  name: "  no_qty",
                  type: "uint32",
                  desc: "NO contracts held",
                },
              ]}
            />
          </SubSection>
        </Section>

        {/* BUY_FLAG */}
        <Section title="BUY_FLAG (0x50)" delay={3}>
          <P>
            Spend <Code>10,000,000</Code> units ($1,000.00) to receive the
            flag. Requires sufficient balance.
          </P>
          <SubSection title="Request">
            <WireFormat
              fields={[{ name: "type", type: "uint8", value: "0x50" }]}
            />
          </SubSection>
          <SubSection title="Response">
            <WireFormat
              fields={[
                { name: "status", type: "uint8", value: "0x00" },
                {
                  name: "flag_len",
                  type: "uint16",
                  desc: "Length of flag string",
                },
                { name: "flag", type: "N bytes", desc: "The flag" },
              ]}
            />
          </SubSection>
        </Section>

        {/* Status Codes */}
        <Section title="Status Codes" delay={3}>
          <Table
            headers={["Code", "Name", "Description"]}
            rows={[
              ["0x00", "OK", "Success"],
              ["0x01", "ERR_INVALID_REQUEST", "Malformed or unknown request"],
              ["0x02", "ERR_NOT_AUTHENTICATED", "Must login first"],
              ["0x03", "ERR_COOLDOWN", "Trade cooldown active"],
              ["0x04", "ERR_STALE", "Quote too old, echo a more recent one"],
              ["0x05", "ERR_INSUFFICIENT_FUNDS", "Not enough balance"],
              ["0x06", "ERR_INSUFFICIENT_POSITION", "Not enough contracts to sell"],
              ["0x07", "ERR_INVALID_QTY", "Quantity is zero"],
              ["0x08", "ERR_MARKET_WARMUP", "Market is still initializing"],
              ["0x09", "ERR_TICKER_NOT_FOUND", "Unknown ticker or not in that snapshot"],
              ["0x0A", "ERR_INVALID_CREDENTIALS", "Wrong username or password"],
              ["0x0B", "ERR_USERNAME_TAKEN", "Username already registered"],
              ["0x0C", "ERR_WEAK_PASSWORD", "Password does not meet requirements"],
              ["0x0D", "ERR_ALREADY_LOGGED_IN", "Another active session for this user"],
              ["0x0E", "ERR_INVALID_QUOTE", "Quote HMAC failed verification"],
              ["0x0F", "ERR_RESEND_UNAVAILABLE", "Requested seq is outside the resend window"],
              ["0x10", "ERR_TICKER_RESOLVED", "Quote price is inside the resolution band"],
            ]}
          />
        </Section>


      </div>

      <div className="h-20" />
    </div>
  );
}

// --- Reusable components ---

function Section({
  title,
  delay,
  children,
}: {
  title: string;
  delay: number;
  children: React.ReactNode;
}) {
  return (
    <section
      className={`animate-slide-up stagger-${Math.min(delay, 6)}`}
    >
      <h2 className="text-xl font-bold text-white mb-4 pb-3 border-b border-border">
        {title}
      </h2>
      {children}
    </section>
  );
}

function SubSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mt-4">
      <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
        {title}
      </h3>
      {children}
    </div>
  );
}

function P({ children }: { children: React.ReactNode }) {
  return <p className="text-sm text-text-dim leading-relaxed mt-2">{children}</p>;
}

function Hl({ children }: { children: React.ReactNode }) {
  return <span className="text-white font-medium">{children}</span>;
}

function Code({ children }: { children: React.ReactNode }) {
  return (
    <code className="px-1.5 py-0.5 bg-surface-3 border border-border rounded text-xs font-mono text-primary">
      {children}
    </code>
  );
}

function Table({
  headers,
  rows,
}: {
  headers: string[];
  rows: string[][];
}) {
  return (
    <div className="mt-3 overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-surface-2">
            {headers.map((h, i) => (
              <th
                key={i}
                className="text-left text-xs text-muted uppercase tracking-wider font-medium px-4 py-2.5"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr
              key={ri}
              className="border-t border-border/50 hover:bg-surface-2/50 transition-colors"
            >
              {row.map((cell, ci) => (
                <td
                  key={ci}
                  className={`px-4 py-2.5 ${ci === 0 ? "font-mono text-primary text-xs" : "text-text-dim"}`}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function WireFormat({
  fields,
  total,
}: {
  fields: {
    name: string;
    type: string;
    value?: string;
    desc?: string;
  }[];
  total?: number;
}) {
  return (
    <div className="mt-2 overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-surface-2">
            <th className="text-left text-xs text-muted uppercase tracking-wider font-medium px-4 py-2">
              Field
            </th>
            <th className="text-left text-xs text-muted uppercase tracking-wider font-medium px-4 py-2">
              Type
            </th>
            <th className="text-left text-xs text-muted uppercase tracking-wider font-medium px-4 py-2">
              Info
            </th>
          </tr>
        </thead>
        <tbody>
          {fields.map((f, i) => (
            <tr
              key={i}
              className="border-t border-border/50"
            >
              <td className="px-4 py-2 font-mono text-xs text-yes/80">
                {f.name}
              </td>
              <td className="px-4 py-2 font-mono text-xs text-muted">
                {f.type}
              </td>
              <td className="px-4 py-2 text-text-dim text-xs">
                {f.value ? (
                  <code className="px-1.5 py-0.5 bg-surface-3 rounded text-primary font-mono">
                    {f.value}
                  </code>
                ) : null}
                {f.value && f.desc ? " · " : null}
                {f.desc}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {total !== undefined && (
        <div className="px-4 py-2 border-t border-border/50 text-xs text-muted bg-surface-2">
          Total: {total} bytes
        </div>
      )}
    </div>
  );
}
