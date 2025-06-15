import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, AuthContextType } from '../types'
import { authAPI } from '../services/api'
import { startTokenRefreshTimer } from '../utils/tokenManager'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authAPI.getMe()
          setUser(userData)
          
          // 로그인 상태에서 토큰 자동 갱신 타이머 시작
          const timerId = startTokenRefreshTimer()
          
          // 컴포넌트 언마운트 시 타이머 정리
          return () => {
            clearInterval(timerId)
          }
        } catch (error) {
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          setToken(null)
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [token])

  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login(username, password)
      const { access_token, refresh_token } = response
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      setToken(access_token)
      
      const userData = await authAPI.getMe()
      setUser(userData)
      
      // 로그인 후 원래 페이지로 리다이렉트
      const redirectPath = localStorage.getItem('redirectAfterLogin')
      if (redirectPath) {
        localStorage.removeItem('redirectAfterLogin')
        window.location.href = redirectPath
      }
    } catch (error) {
      throw error
    }
  }

  const register = async (username: string, email: string, password: string) => {
    try {
      await authAPI.register(username, email, password)
      // 회원가입 후 자동 로그인
      await login(username, password)
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    setToken(null)
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    isLoading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
} 