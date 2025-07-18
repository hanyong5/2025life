import React, { useEffect, useState } from "react";

const DATA_URL = "https://hanyong5.github.io/2025life/cgntv_crawl_result.json";

function App() {
  const [cgntvData, setCgntvData] = useState([]);
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(DATA_URL)
      .then((res) => res.json())
      .then((data) => {
        setCgntvData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const openVideoInNewTab = () => {
    if (currentVideoUrl) {
      window.open(currentVideoUrl, "_blank");
    }
  };

  if (loading) return <div className="p-8 text-center">로딩 중...</div>;
  if (!cgntvData.length)
    return <div className="p-8 text-center">데이터 없음</div>;

  const currentVideo = cgntvData[currentVideoIndex];
  const currentVideoUrl = currentVideo?.vod_data?.startsWith("http")
    ? currentVideo.vod_data
    : currentVideo?.vod_data
    ? (currentVideo.vod_data.startsWith("//") ? "http:" : "") +
      currentVideo.vod_data
    : "";

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* <video
          src={currentVideoUrl}
          className="w-full rounded-lg shadow-md"
          style={{
            aspectRatio: "16 / 9",
            width: "100%",
            border: "none",
            maxHeight: "70vh",
          }}
          title="CGNTV 영상 재생"
          controls
          autoPlay
        >
          브라우저가 video 태그를 지원하지 않습니다.
        </video> */}
        <button
          onClick={openVideoInNewTab}
          className="bg-blue-500 text-white px-4 py-2 rounded-md w-full"
        >
          새 탭에서 영상 열기
        </button>
        <div className="pt-5"></div>
        <div className="mb-6 text-center">
          <h2 className="text-xl font-semibold mb-2 text-gray-800">
            {currentVideo.pTitle}
          </h2>
          <p className="text-xl text-gray-600 mb-2 font-bold ">
            {currentVideo.content_date?.date}{" "}
            {currentVideo.content_date?.weekday_kr}
          </p>
        </div>
        {/* 영상 목록 */}
        {/* <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">
            영상 목록 ({cgntvData.length}개)
          </h3>
          <div className="space-y-2">
            {cgntvData.map((video, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  index === currentVideoIndex
                    ? "bg-blue-100 border-l-4 border-blue-500"
                    : "bg-gray-50 hover:bg-gray-100"
                }`}
                onClick={() => setCurrentVideoIndex(index)}
              >
                <h4 className="font-medium text-gray-800">{video.pTitle}</h4>
                <p className="text-sm text-gray-600">
                  {video.content_date?.date} {video.content_date?.weekday_kr}
                </p>
              </div>
            ))}
          </div>
        </div> */}
        {/* 영상 설명 */}
        {currentVideo.contArea_content && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">
              오늘의 큐티
            </h3>
            <div
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{
                __html: currentVideo.contArea_content,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
