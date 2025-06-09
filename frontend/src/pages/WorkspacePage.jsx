import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import { FolderIcon, FileIcon, UploadIcon, PlayIcon } from 'lucide-react'

const WorkspacePage = () => {
  const { id } = useParams()
  const [currentPath, setCurrentPath] = useState('')
  const [files, setFiles] = useState([
    { name: 'notebooks', is_directory: true, size: 0, path: 'notebooks' },
    { name: 'data', is_directory: true, size: 0, path: 'data' },
    { name: 'outputs', is_directory: true, size: 0, path: 'outputs' },
    { name: 'Welcome.ipynb', is_directory: false, size: 2048, path: 'Welcome.ipynb' }
  ])

  // 임시 워크스페이스 정보
  const workspace = {
    id: id,
    name: 'My Data Project',
    description: 'Python 데이터 분석 프로젝트',
    is_running: false
  }

  const handleFileClick = (file) => {
    if (file.is_directory) {
      // 폴더 탐색
      setCurrentPath(file.path)
      // TODO: API 호출로 폴더 내용 로드
    } else {
      // 파일 열기
      if (file.name.endsWith('.ipynb')) {
        // Jupyter Notebook 열기
        window.open(`http://localhost:8888/notebooks/${file.path}`, '_blank')
      }
    }
  }

  const handleUpload = (event) => {
    const files = Array.from(event.target.files)
    // TODO: API 호출로 파일 업로드
    console.log('Uploading files:', files)
  }

  const handleStartJupyter = () => {
    // TODO: API 호출로 Jupyter 시작
    console.log('Starting Jupyter for workspace:', id)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '-'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 워크스페이스 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{workspace.name}</h1>
            <p className="text-gray-600 mt-2">{workspace.description}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleStartJupyter}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <PlayIcon size={20} />
              Jupyter Lab 시작
            </button>
          </div>
        </div>
      </div>

      {/* 파일 관리 섹션 */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">파일 관리</h2>
            <div className="flex gap-3">
              <label className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 cursor-pointer flex items-center gap-2">
                <UploadIcon size={20} />
                파일 업로드
                <input
                  type="file"
                  multiple
                  className="hidden"
                  onChange={handleUpload}
                />
              </label>
              <button className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
                새 폴더
              </button>
            </div>
          </div>
          
          {/* 경로 표시 */}
          <div className="mt-4 text-sm text-gray-600">
            경로: /{currentPath}
          </div>
        </div>

        {/* 파일 목록 */}
        <div className="p-6">
          <div className="grid gap-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer border"
                onClick={() => handleFileClick(file)}
              >
                <div className="flex items-center gap-3">
                  {file.is_directory ? (
                    <FolderIcon className="text-yellow-600" size={24} />
                  ) : (
                    <FileIcon className="text-blue-600" size={24} />
                  )}
                  <div>
                    <div className="font-medium text-gray-900">{file.name}</div>
                    <div className="text-sm text-gray-500">
                      {file.is_directory ? '폴더' : formatFileSize(file.size)}
                    </div>
                  </div>
                </div>
                
                {!file.is_directory && (
                  <div className="flex gap-2">
                    <button
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      onClick={(e) => {
                        e.stopPropagation()
                        // TODO: 파일 다운로드
                      }}
                    >
                      다운로드
                    </button>
                    <button
                      className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                      onClick={(e) => {
                        e.stopPropagation()
                        // TODO: 파일 삭제
                      }}
                    >
                      삭제
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Jupyter 상태 */}
      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Jupyter Lab 상태</h3>
        <div className="flex items-center gap-4">
          <div className={`w-3 h-3 rounded-full ${workspace.is_running ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-gray-700">
            {workspace.is_running ? 'Jupyter Lab이 실행 중입니다' : 'Jupyter Lab이 중지되어 있습니다'}
          </span>
          {workspace.is_running && (
            <a
              href="http://localhost:8888"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-600 hover:text-indigo-800 underline"
            >
              Jupyter Lab 열기 →
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

export default WorkspacePage 