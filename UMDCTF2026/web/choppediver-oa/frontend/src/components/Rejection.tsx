export function Rejection({ reason: _reason }: { reason: string }) {
  const now = new Date();
  const stamp = now.toLocaleString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

  return (
    <div className="min-h-screen bg-[#f6f8fc] text-[#202124] flex items-start justify-center py-16 px-6">
      <div
        className="w-full max-w-[820px] fade-up"
        style={{ fontFamily: 'Arial, "Helvetica Neue", Helvetica, sans-serif' }}
      >
        {/* Subject */}
        <h1 className="text-[22px] font-normal text-[#202124] mb-6 tracking-[0.01em]">
          Thank You from Choppediver
        </h1>

        {/* Sender row */}
        <div className="flex items-start gap-3 mb-7">
          <div className="w-10 h-10 rounded-full bg-[#0b57d0] text-white flex items-center justify-center text-[16px] font-medium shrink-0 mt-0.5">
            C
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline flex-wrap gap-x-2 gap-y-0.5">
              <span className="text-[14px] font-bold text-[#202124]">
                Choppediver Recruitment
              </span>
              <span className="text-[13px] text-[#5f6368]">
                &lt;recruiting@choppediver.com&gt;
              </span>
            </div>
            <div className="text-[12px] text-[#5f6368] mt-0.5">
              to me <span className="mx-1">·</span> {stamp}
            </div>
          </div>
        </div>

        {/* Body */}
        <div
          className="text-[#202124] text-[14px] leading-[1.58] space-y-4"
          style={{ maxWidth: "680px" }}
        >
          <p>Dear candidate,</p>

          <p>
            Thank you for your effort in completing the assessment for the
            Software Engineer Intern position. We appreciate the time you
            invested in this process. However, after careful review and
            consideration, we have made the decision not to proceed with your
            candidacy at this time.
          </p>

          <p>
            With that said, we'd like to maintain your information in our
            database to contact you in the future, should a more pertinent
            position arise.
          </p>

          <p className="italic">
            Additionally, we kindly request that you wait for a period of 1
            year before reapplying for the same position. This timeframe will
            allow you to develop the skills and experiences necessary for
            future success. Please note that any applications received within
            the 1-year timeframe will be automatically rejected.
          </p>

          <p>
            We wish you all the best in your future endeavors and remain open
            to the possibility of reconnecting with you down the line.
          </p>

          <p className="pt-2">
            Best,
            <br />
            <br />
            Choppediver Recruitment
          </p>
        </div>

      </div>
    </div>
  );
}
