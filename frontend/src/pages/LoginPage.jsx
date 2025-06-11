import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(formData.email, formData.password)
      
      // 모든 사용자는 로그인 후 Main Page로 이동
      navigate('/main')
    } catch (err) {
      setError('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative overflow-hidden">
      {/* 배경 장식 */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5"></div>
        <div className="absolute top-20 left-20 w-72 h-72 bg-blue-400/10 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-72 h-72 bg-purple-400/10 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute -bottom-32 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-pink-400/10 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col">
        {/* 헤더 */}
        <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <span className="text-white text-xl font-bold">G</span>
                </div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Genba X
                </h1>
              </div>
            </div>
          </div>
        </header>

        {/* 메인 콘텐츠 */}
        <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
          <div className="max-w-md w-full">
            {/* 로그인 카드 */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl border border-white/50 p-8 transform hover:scale-105 transition-all duration-300">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  로그인
                </h2>
                <p className="text-gray-600">
                  Genba X 플랫폼에 접속하세요
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
                    <div className="flex items-center">
                      <span className="text-red-500 mr-2">⚠️</span>
                      {error}
                    </div>
                  </div>
                )}

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    이메일
                  </label>
                  <div className="relative">
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                      placeholder="이메일을 입력하세요"
                      value={formData.email}
                      onChange={handleChange}
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                      <span className="text-gray-400">📧</span>
                    </div>
                  </div>
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    비밀번호
                  </label>
                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type="password"
                      required
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                      placeholder="비밀번호를 입력하세요"
                      value={formData.password}
                      onChange={handleChange}
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                      <span className="text-gray-400">🔒</span>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 shadow-lg"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      로그인 중...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <span className="mr-2">🚀</span>
                      로그인
                    </div>
                  )}
                </button>

                <div className="text-center pt-4">
                  <Link 
                    to="/register" 
                    className="text-blue-600 hover:text-purple-600 font-medium transition-colors duration-200"
                  >
                    계정이 없으신가요? 회원가입
                  </Link>
                </div>
              </form>
            </div>

            {/* 추가 기능 카드들 */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link to="/register" className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-white/30 hover:bg-white/80 transition-all duration-300 transform hover:scale-105 cursor-pointer">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <span className="text-green-600">✨</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">회원가입</h3>
                    <p className="text-xs text-gray-500">새 계정 만들기</p>
                  </div>
                </div>
              </Link>

              <Link to="/reset-password" className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-white/30 hover:bg-white/80 transition-all duration-300 transform hover:scale-105 cursor-pointer">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                    <span className="text-orange-600">🔑</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">비밀번호 초기화</h3>
                    <p className="text-xs text-gray-500">비밀번호를 잊으셨나요?</p>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage 