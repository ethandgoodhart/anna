

const Widgets = () => {
  const [notifications, setNotifications] = React.useState([]);

  React.useEffect(() => {
    const handleWebhook = (event, { serviceName, data }) => {
      console.log(serviceName, data);
      if (serviceName === 'music') {
        setNotifications(prev => [...prev, { type: 'music', data, timestamp: Date.now() }]);
      } else if (serviceName === 'notification') {
        setNotifications(prev => [...prev, { type: 'notification', data, timestamp: Date.now() }]);
      }
    };

    const cleanupInterval = setInterval(() => {
      const now = Date.now();
      setNotifications(prev => prev.filter(n => now - n.timestamp < 10000));
    }, 1000);

    window.ipcRenderer.on('webhook-event', handleWebhook);
    return () => {
      window.ipcRenderer.removeListener('webhook-event', handleWebhook);
      clearInterval(cleanupInterval);
    };
  }, []);

  return (
    <div
      style={{
        position: "fixed",
        bottom: "80px", 
        left: "50%",
        transform: "translateX(-50%)",
        padding: "8px 16px",
        borderRadius: "4px",
        perspective: "2000px",
        transformStyle: "preserve-3d",
        animation: "float 6s ease-in-out infinite"
      }}
    >
      <style>
        {`
          @keyframes float {
            0%, 100% { transform: translateX(-50%) translateY(0px); }
            50% { transform: translateX(-50%) translateY(-20px); }
          }
          
          @keyframes glow {
            0%, 100% { filter: drop-shadow(0 0 15px rgba(0,255,255,0.3)); }
            50% { filter: drop-shadow(0 0 25px rgba(0,255,255,0.5)); }
          }

          @keyframes slideIn {
            from { 
              opacity: 0;
              transform: translateY(50px) scale(0.8);
            }
            to {
              opacity: 1; 
              transform: translateY(0) scale(1);
            }
          }

          .notification-enter {
            animation: slideIn 0.5s cubic-bezier(0.23, 1, 0.32, 1) forwards;
          }

          .hologram-effect {
            position: relative;
            overflow: hidden;
          }

          .hologram-effect::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 50%;
            height: 100%;
            background: linear-gradient(
              90deg,
              transparent,
              rgba(255, 255, 255, 0.2),
              transparent
            );
            animation: hologramScan 3s linear infinite;
          }

          @keyframes hologramScan {
            0% { left: -100%; }
            100% { left: 200%; }
          }
        `}
      </style>
      <div className="flex flex-col gap-4" style={{ transformStyle: "preserve-3d" }}>
        {notifications.map((notification, index) => {
          const stackOffset = (notifications.length - 1 - index) * 20;
          const transform = `translateZ(${stackOffset}px) translateY(-${stackOffset}px)`;
          
          if (notification.type === 'notification') {
            return (
              <div key={notification.timestamp} className="notification-enter">
                <NotificationCard 
                  userName={notification.data.userName}
                  message={notification.data.message}
                  notificationCount={notification.data.notificationCount}
                  style={{ transform }}
                />
              </div>
            );
          } else if (notification.type === 'music') {
            return (
              <div key={notification.timestamp} className="notification-enter">
                <MusicPlayerNotification 
                  songTitle={notification.data.songTitle}
                  artist={notification.data.artist}
                  currentTime={notification.data.currentTime}
                  duration={notification.data.duration}
                  progress={notification.data.progress}
                  albumArt={notification.data.albumArt}
                  style={{ transform }}
                />
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
};

const NotificationCard = ({
  userName,
  message,
  notificationCount,
}) => {
  return (
    <div
      className={
        "hologram-effect relative flex w-[562px] h-[131px] items-center gap-7 px-8 py-8 rounded-[40px] bg-[#1c1c1c]/30 backdrop-blur-[50px]"
      }
      style={{
        transform: "translateZ(40px) rotateX(5deg)",
        boxShadow: "0 20px 50px rgba(0,0,0,0.5), 0 0 60px rgba(0,255,255,0.1) inset",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        transformStyle: "preserve-3d",
        backfaceVisibility: "hidden",
        border: "1px solid rgba(0,255,255,0.1)",
        animation: "glow 3s ease-in-out infinite"
      }}
    >
      <div className="relative" style={{ transform: "translateZ(30px)" }}>
        <div className="relative w-[60px] h-[60px] bg-[#949ba9]/50 rounded-full flex items-center justify-center"
             style={{ 
               boxShadow: "0 8px 32px rgba(0,255,255,0.2)",
               transform: "translateZ(20px)",
               transition: "transform 0.3s ease"
             }}>
          <span className="text-[32px]" style={{ transform: "translateZ(10px)" }}>🌲</span>
        </div>

        <div className="absolute -top-1 right-0" style={{ transform: "translateZ(25px)" }}>
          <div className="relative flex items-center justify-center w-5 h-5 bg-[#1b1e23] rounded-full shadow-[0px_8px_16px_0px_rgba(0,255,255,0.3)] border border-[#00ffff]/30">
            <span className="text-[#00ffff] text-base font-normal">
              {notificationCount}
            </span>
          </div>
        </div>

        <img
          src="https://storage.googleapis.com/tempo-public-images/figma-exports%2Fgithub%7C63950637-1739664807302-node-11%3A42-1739664806941.png"
          alt="Message notification"
          className="absolute -bottom-1 -right-1 w-[23px] h-[23px]"
          style={{ 
            filter: "drop-shadow(0 4px 16px rgba(0,255,255,0.4))",
            transform: "translateZ(15px)"
          }}
        />
      </div>

      <div className="flex flex-col gap-1" style={{ transform: "translateZ(20px)" }}>
        <h3 className="text-[26px] text-[#ececec] font-['SF Pro'] font-normal"
            style={{ textShadow: "0 4px 8px rgba(0,255,255,0.3)" }}>
          {userName}
        </h3>
        <p className="text-2xl text-[#ececec] font-['SF Pro'] font-normal"
           style={{ textShadow: "0 2px 4px rgba(0,255,255,0.3)" }}>
          {message}
        </p>
      </div>
    </div>
  );
};

function MusicPlayerNotification({
  songTitle,
  artist,
  currentTime: initialTimeMs,
  duration: durationMs,
  progress: initialProgress,
  albumArt,
}) {
  const [elapsedMs, setElapsedMs] = React.useState(initialTimeMs);
  const [progress, setProgress] = React.useState(initialProgress);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setElapsedMs(prev => {
        if (prev >= durationMs) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1000;
      });

      setProgress(prev => {
        const newProgress = (elapsedMs / durationMs) * 100;
        return Math.min(newProgress, 100);
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [durationMs, elapsedMs]);

  const formatTime = (ms) => {
    if (!ms || isNaN(ms)) return "0:00";
    const totalSeconds = Math.floor(ms / 1000);
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className={
        "hologram-effect relative flex flex-col w-[551px] h-[234px] p-6 rounded-[40px] bg-[#2a2a2a]/70 backdrop-blur-[50px]"
      }
      style={{
        transform: "translateZ(40px) rotateX(5deg)",
        boxShadow: "0 25px 60px rgba(0,0,0,0.5), 0 0 70px rgba(0,255,255,0.1) inset",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        transformStyle: "preserve-3d",
        backfaceVisibility: "hidden",
        border: "1px solid rgba(0,255,255,0.1)",
        animation: "glow 3s ease-in-out infinite"
      }}
    >
      <div className="flex items-start gap-6 mb-8" style={{ transform: "translateZ(30px)" }}>
        <img
          src={albumArt}
          alt="Album artwork"
          className="w-[75px] h-[75px] rounded-lg"
          style={{ 
            boxShadow: "0 8px 32px rgba(0,255,255,0.2)",
            transform: "translateZ(20px)",
            transition: "transform 0.3s ease"
          }}
        />
        <div className="flex flex-col gap-1" style={{ transform: "translateZ(15px)" }}>
          <h3 className="text-2xl text-white font-bold font-['SF Pro']"
              style={{ textShadow: "0 4px 8px rgba(0,255,255,0.3)" }}>
            {songTitle}
          </h3>
          <p className="text-xl text-[#9f9f9f] font-normal font-['SF Pro']"
             style={{ textShadow: "0 2px 4px rgba(0,255,255,0.3)" }}>
            {artist}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4 px-3" style={{ transform: "translateZ(20px)" }}>
        <span className="text-base text-[#9f9f9f] font-['SF Pro'] w-[45px]">
          {formatTime(elapsedMs)}
        </span>
        <div className="relative flex-1 h-3" style={{ transform: "translateZ(10px)" }}>
          <div className="absolute w-full h-full bg-[#9f9f9f]/20 rounded-[10px]"
               style={{ boxShadow: "inset 0 2px 6px rgba(0,255,255,0.1)" }}></div>
          <div
            className="absolute h-full bg-[#00ffff]/30 rounded-l-[10px]"
            style={{ 
              width: `${progress}%`,
              boxShadow: "0 2px 6px rgba(0,255,255,0.3)",
              transition: "width 0.3s ease"
            }}
          ></div>
        </div>
        <span className="text-base text-[#9f9f9f] font-['SF Pro'] w-[45px]">{formatTime(durationMs - elapsedMs)}</span>
      </div>

      <div className="flex justify-center items-center gap-12" style={{ transform: "translateZ(25px)" }}>
        <button
          className="text-[#00ffff] transform rotate-180 hover:scale-110 transition-all duration-300"
          aria-label="Previous track"
          style={{ 
            filter: "drop-shadow(0 4px 8px rgba(0,255,255,0.3))",
            transform: "translateZ(15px)"
          }}
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
        <button 
          className="flex gap-[13px] h-[46px] hover:scale-110 transition-all duration-300" 
          aria-label="Pause"
          style={{ 
            filter: "drop-shadow(0 4px 8px rgba(0,255,255,0.3))",
            transform: "translateZ(15px)"
          }}>
          <div className="w-3.5 h-full bg-[#00ffff] rounded-[5px]"></div>
          <div className="w-3.5 h-full bg-[#00ffff] rounded-[5px]"></div>
        </button>
        <button 
          className="text-[#00ffff] hover:scale-110 transition-all duration-300" 
          aria-label="Next track"
          style={{ 
            filter: "drop-shadow(0 4px 8px rgba(0,255,255,0.3))",
            transform: "translateZ(15px)"
          }}>
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

const root = ReactDOM.createRoot(document.getElementById("react-container"));
root.render(<Widgets />);
