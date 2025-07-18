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

  const currentVideo = cgntvData[currentVideoIndex];
  const currentVideoUrl = currentVideo?.vod_data?.startsWith("http")
    ? currentVideo.vod_data
    : currentVideo?.vod_data
    ? (currentVideo.vod_data.startsWith("//") ? "http:" : "") +
      currentVideo.vod_data
    : "";

  const openVideoInNewTab = () => {
    if (currentVideoUrl) {
      window.open(currentVideoUrl, "_blank");
    }
  };

  if (loading) return <div className="p-8 text-center">로딩 중...</div>;
  if (!cgntvData.length)
    return <div className="p-8 text-center">데이터 없음</div>;

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* 앱 타이틀/로고/설명 */}

        {/* 오프라인 안내 */}
        {!navigator.onLine && (
          <div className="bg-yellow-100 text-yellow-800 p-2 text-center rounded mb-4">
            오프라인 상태입니다. 저장된 말씀만 볼 수 있습니다.
          </div>
        )}
        {/* 영상 버튼 */}
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
        {/* 영상 설명 */}
        {currentVideo.contArea_content && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">
              오늘의 큐티
            </h3>
            <div
              className="prose prose-sm max-w-none text-xl"
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
