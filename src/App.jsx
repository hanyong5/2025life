import React, { useState } from "react";
import cgntvData from "./data/cgntv_crawl_result.json";

function App() {
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);

  // 현재 선택된 영상의 URL 가져오기
  const getCurrentVideoUrl = () => {
    if (cgntvData.length === 0) return "";

    const baseUrl = "http:";
    const currentVideo = cgntvData[currentVideoIndex];

    // currentVideo나 vod_data가 없는 경우 처리
    if (!currentVideo || !currentVideo.vod_data) {
      return "";
    }

    // vod_data가 문자열인 경우 직접 사용
    return baseUrl + currentVideo.vod_data;
  };

  const currentVideo = cgntvData[currentVideoIndex] || {};
  const currentVideoUrl = getCurrentVideoUrl();

  // 새 탭에서 영상 열기
  const openVideoInNewTab = () => {
    if (currentVideoUrl) {
      window.open(currentVideoUrl, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        {cgntvData.length > 0 ? (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <video
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
            </video>
            <div className="pt-5"></div>
            {/* 영상 정보 */}
            <div className="mb-6 text-center">
              <h2 className="text-xl font-semibold mb-2 text-gray-800">
                {currentVideo.pTitle}
              </h2>
              <p className="text-sm text-gray-600 mb-2">
                {currentVideo.content_date.date}{" "}
                {currentVideo.content_date.weekday_kr}
              </p>
            </div>

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
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600">영상 데이터를 불러올 수 없습니다.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
