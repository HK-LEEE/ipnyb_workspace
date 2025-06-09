import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { PlusIcon, FolderIcon, PlayIcon, StopIcon } from 'lucide-react'

const DashboardPage = () => {
  const { user } = useAuth()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newWorkspace, setNewWorkspace] = useState({ name: '', description: '' })

  // 임시 워크스페이스 데이터 (나중에 API와 연결)
  const [workspaces, setWorkspaces] = useState([
    {
      id: 1,
      name: 'My First Project',
      description: 'Python 데이터 분석 프로젝트',
      created_at: '2024-01-01',
      is_running: false
    }
  ])

  const handleCreateWorkspace = async (e) => {
    e.preventDefault()
    // TODO: API 호출로 워크스페이스 생성
    const workspace = {
      id: Date.now(),
      name: newWorkspace.name,
      description: newWorkspace.description,
      created_at: new Date().toISOString().split('T')[0],
      is_running: false
    }
    setWorkspaces([...workspaces, workspace])
    setNewWorkspace({ name: '', description: '' })
    setShowCreateModal(false)
  }

  const handleStartJupyter = (workspaceId) => {
    // TODO: API 호출로 Jupyter 시작
    setWorkspaces(workspaces.map(ws => 
      ws.id === workspaceId ? { ...ws, is_running: true } : ws
    ))
  }

  const handleStopJupyter = (workspaceId) => {
    // TODO: API 호출로 Jupyter 중지
    setWorkspaces(workspaces.map(ws => 
      ws.id === workspaceId ? { ...ws, is_running: false } : ws
    ))
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          안녕하세요, {user?.username}님! 👋
        </h1>
        <p className="text-gray-600 mt-2">
          Jupyter Data Platform에서 데이터 분석을 시작해보세요
        </p>
      </div>

      {/* 새 워크스페이스 생성 버튼 */}
      <div className="mb-6">
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <PlusIcon size={20} />
          새 워크스페이스 만들기
        </button>
      </div>

      {/* 워크스페이스 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workspaces.map((workspace) => (
          <div key={workspace.id} className="bg-white rounded-lg shadow-md p-6 border">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <FolderIcon className="text-indigo-600" size={24} />
                <div>
                  <h3 className="font-semibold text-gray-900">{workspace.name}</h3>
                  <p className="text-sm text-gray-600">{workspace.description}</p>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs ${
                workspace.is_running 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {workspace.is_running ? '실행 중' : '중지됨'}
              </span>
            </div>
            
            <div className="text-sm text-gray-500 mb-4">
              생성일: {workspace.created_at}
            </div>

            <div className="flex gap-2">
              {workspace.is_running ? (
                <button
                  onClick={() => handleStopJupyter(workspace.id)}
                  className="flex items-center gap-1 px-3 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm"
                >
                  <StopIcon size={16} />
                  Jupyter 중지
                </button>
              ) : (
                <button
                  onClick={() => handleStartJupyter(workspace.id)}
                  className="flex items-center gap-1 px-3 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm"
                >
                  <PlayIcon size={16} />
                  Jupyter 시작
                </button>
              )}
              
              <button className="px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm">
                파일 관리
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 새 워크스페이스 생성 모달 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold mb-4">새 워크스페이스 생성</h2>
            <form onSubmit={handleCreateWorkspace}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  워크스페이스 이름
                </label>
                <input
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  value={newWorkspace.name}
                  onChange={(e) => setNewWorkspace({...newWorkspace, name: e.target.value})}
                  placeholder="예: 데이터 분석 프로젝트"
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  설명 (선택사항)
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  rows="3"
                  value={newWorkspace.description}
                  onChange={(e) => setNewWorkspace({...newWorkspace, description: e.target.value})}
                  placeholder="프로젝트에 대한 간단한 설명"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex-1 bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700"
                >
                  생성
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-md hover:bg-gray-400"
                >
                  취소
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage 