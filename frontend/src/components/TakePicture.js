import React, { useRef, useState, useEffect } from 'react';

const TakePicture = ({onCapture}) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  // const [capturedImage, setCapturedImage] = useState(null);
  const [isCameraOn, setIsCameraOn] = useState(false);

  useEffect(() => {
    const startCamera = async () => {
      try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { aspectRatio: { ideal: 4 / 3 }, width: { ideal: 3264 }, height: { ideal: 2448 } }
      });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsCameraOn(true);
        }
      } catch (err) {
        console.error("카메라 접근 실패:", err);
        setIsCameraOn(false);
      }
    };

    startCamera();
  }, []);

  const captureImage = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    const vw = video.videoWidth;
    const vh = video.videoHeight;

    console.log('Video resolution:', vw, vh);

    canvas.width = vw;
    canvas.height = vh;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, vw, vh);

    const imageDataUrl = canvas.toDataURL('image/png');

    if (onCapture) {
      onCapture(imageDataUrl);
    }
  };

  useEffect(() => {
    const listener = () => captureImage();
    window.addEventListener("trigger-camera-capture", listener);
    return () => window.removeEventListener("trigger-camera-capture", listener);
  }, []);


  return (
    <div className="flex flex-col gap-lg mt-md">
      <div className="flex gap-lg flex-wrap">

        <div className="flex-1 min-w-[300px] bg-surface rounded-md shadow-md overflow-hidden">
          <h3 className="p-md bg-primary text-white m-0 flex items-center justify-between">
            <span>카메라 화면</span>
            {isCameraOn && (
              <span className="bg-red-600 text-white text-xs font-bold px-2 py-1 rounded shadow-md animate-pulse">
                ● ON AIR
              </span>
            )}
          </h3>
          <div className="p-md flex justify-center items-center bg-gray-300 overflow-hidden min-h-[600px] aspect-[4/3] w-full max-w-[960px]">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="object-contain min-w-[400px] h-[600px] transform -rotate-90 origin-center"
            />
          </div>
          <div className="p-md flex justify-end">
            <button
              onClick={captureImage}
              className="px-4 py-2 bg-primary text-white font-semibold rounded-md shadow hover:bg-primary-dark transition duration-200"
            >
            촬영하기
            </button>
          </div>
        </div>

      </div>
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default TakePicture;
