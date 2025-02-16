const NotificationCard = ({
  userName = "Ethan Goodhart Stanford",
  message = "Yoo do you wanna hike the dish?",
  notificationCount = 2,
}) => {
  return (
    <div
      className={
        "relative flex w-[562px] h-[131px] items-center gap-7 px-8 py-8 rounded-[40px] bg-[#1c1c1c]/50 backdrop-blur-[50px]"
      }
    >
      {/* Avatar Container */}
      <div className="relative">
        {/* Avatar */}
        <div className="relative w-[60px] h-[60px] bg-[#949ba9] rounded-full flex items-center justify-center">
          <span className="text-[32px]">🌲</span>
        </div>

        {/* Notification Badge */}
        <div className="absolute -top-1 right-0">
          <div className="relative flex items-center justify-center w-5 h-5 bg-[#1b1e23] rounded-full shadow-[0px_4px_10px_0px_rgba(0,0,0,0.25)] border border-[#969b9f]">
            <span className="text-[#969b9f] text-base font-normal">
              {notificationCount}
            </span>
          </div>
        </div>

        {/* Message Icon */}
        <img
          src="https://storage.googleapis.com/tempo-public-images/figma-exports%2Fgithub%7C63950637-1739664807302-node-11%3A42-1739664806941.png"
          alt="Message notification"
          className="absolute -bottom-1 -right-1 w-[23px] h-[23px]"
        />
      </div>

      {/* Text Content */}
      <div className="flex flex-col gap-1">
        <h3 className="text-[26px] text-[#ececec] font-['SF Pro'] font-normal">
          {userName}
        </h3>
        <p className="text-2xl text-[#ececec] font-['SF Pro'] font-normal">
          {message}
        </p>
      </div>
    </div>
  );
};

function MusicPlayerNotification({
  songTitle = "Not Like Us",
  artist = "Kendrick Lamar",
  currentTime = "0:08",
  duration = "4:26",
  progress = 6,
  albumArt = "https://storage.googleapis.com/tempo-public-images/figma-exports%2Fgithub%7C63950637-1739665490970-node-11%3A64-1739665490217.png",
}) {
  return (
    <div
      className={
        "relative flex flex-col w-[551px] h-[234px] p-6 rounded-[40px] bg-[#1c1c1c]/50 backdrop-blur-[50px]"
      }
    >
      {/* Song Info */}
      <div className="flex items-start gap-6 mb-8">
        <img
          src={albumArt}
          alt="Album artwork"
          className="w-[75px] h-[75px] rounded-lg"
        />
        <div className="flex flex-col gap-1">
          <h3 className="text-2xl text-white font-bold font-['SF Pro']">
            {songTitle}
          </h3>
          <p className="text-xl text-[#9f9f9f] font-normal font-['SF Pro']">
            {artist}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="flex items-center gap-2 mb-4 px-3">
        <span className="text-base text-[#9f9f9f] font-['SF Pro'] w-[45px]">
          {currentTime}
        </span>
        <div className="relative flex-1 h-3">
          <div className="absolute w-full h-full bg-[#9f9f9f]/50 rounded-[10px]"></div>
          <div
            className="absolute h-full bg-[#e3e3e3]/50 rounded-l-[10px]"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <span className="text-base text-[#9f9f9f] font-['SF Pro'] w-[45px]">{`-${duration}`}</span>
      </div>

      {/* Controls */}
      <div className="flex justify-center items-center gap-12">
        <button
          className="text-white transform rotate-180"
          aria-label="Previous track"
        >
          <svg
            className="w-[70px] h-[42px]"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path d="M3.288 4.818A1.5 1.5 0 0 0 1 6.095v7.81a1.5 1.5 0 0 0 2.288 1.276l6.323-3.905c.155-.096.285-.213.389-.344v2.973a1.5 1.5 0 0 0 2.288 1.276l6.323-3.905a1.5 1.5 0 0 0 0-2.552l-6.323-3.906A1.5 1.5 0 0 0 10 6.095v2.972a1.506 1.506 0 0 0-.389-.343L3.288 4.818Z" />
          </svg>
        </button>
        <button className="flex gap-[13px] h-[46px]" aria-label="Pause">
          <div className="w-3.5 h-full bg-white rounded-[5px]"></div>
          <div className="w-3.5 h-full bg-white rounded-[5px]"></div>
        </button>
        <button className="text-white" aria-label="Next track">
        <svg
            className="w-[70px] h-[42px]"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path d="M3.288 4.818A1.5 1.5 0 0 0 1 6.095v7.81a1.5 1.5 0 0 0 2.288 1.276l6.323-3.905c.155-.096.285-.213.389-.344v2.973a1.5 1.5 0 0 0 2.288 1.276l6.323-3.905a1.5 1.5 0 0 0 0-2.552l-6.323-3.906A1.5 1.5 0 0 0 10 6.095v2.972a1.506 1.506 0 0 0-.389-.343L3.288 4.818Z" />
          </svg>
        </button>
      </div>
    </div>
  );
}

const MyComponent = () => {
  return (
    <div
      style={{
        position: "absolute",
        bottom: "80px",
        left: "50%",
        transform: "translateX(-50%)",
        padding: "8px 16px",
        borderRadius: "4px",
      }}
    >
      <div className="flex flex-col gap-4">
        <NotificationCard />
        <MusicPlayerNotification />
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById("react-container"));
root.render(<MyComponent />);
