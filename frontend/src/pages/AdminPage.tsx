import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface User {
  id: string;
  real_name: string;
  display_name?: string;
  email: string;
  phone_number?: string;
  department?: string;
  position?: string;
  bio?: string;
  is_active: boolean;
  is_admin: boolean;
  approval_status: string;
  approval_note?: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  last_login_at?: string;
  login_count: number;
  role?: any;
  group?: {
    id: number;
    name: string;
    description?: string;
  };
  permissions?: any[];
  features?: any[];
}

interface GroupUser {
  id: string;
  real_name: string;
  display_name?: string;
  email: string;
  phone_number?: string;
  department?: string;
  position?: string;
  is_active: boolean;
  is_admin: boolean;
  is_verified: boolean;
  approval_status: string;
  created_at: string;
  last_login_at?: string;
  login_count: number;
  role_name?: string;
}

interface Group {
  id: number;
  name: string;
  description: string;
  users_count?: number;
  features?: Feature[];
  permissions?: any[];
  users?: GroupUser[];
  created_by?: string;
  created_at?: string;
}

interface Feature {
  id: number;
  name: string;
  display_name: string;
  description: string;
  category: string;
  icon: string;
  url_path: string;
  is_active: boolean;
  requires_approval: boolean;
  is_external?: boolean;
  open_in_new_tab?: boolean;
}

const AdminPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'users' | 'features' | 'groups'>('dashboard');
  const [users, setUsers] = useState<User[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [features, setFeatures] = useState<Feature[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUserModal, setShowUserModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [isEditingUserInfo, setIsEditingUserInfo] = useState(false);
  const [passwordData, setPasswordData] = useState({
    user_id: '',
    new_password: ''
  });
  const [editedUserInfo, setEditedUserInfo] = useState({
    real_name: '',
    display_name: '',
    phone_number: '',
    department: '',
    position: '',
    bio: ''
  });
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null);
  const [showFeatureModal, setShowFeatureModal] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<Feature | null>(null);
  const [isEditingFeature, setIsEditingFeature] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [editedFeatureInfo, setEditedFeatureInfo] = useState({
    name: '',
    display_name: '',
    description: '',
    category: '',
    icon: '',
    url_path: '',
    is_active: true,
    requires_approval: false,
    is_external: false,
    open_in_new_tab: false
  });
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [isEditingGroup, setIsEditingGroup] = useState(false);
  const [editedGroupInfo, setEditedGroupInfo] = useState({
    name: '',
    description: ''
  });
  const [selectedGroupFeatures, setSelectedGroupFeatures] = useState<number[]>([]);
  const [availableFeatures, setAvailableFeatures] = useState<Feature[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }
    
    fetchData();
  }, [navigate]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [usersRes, groupsRes, featuresRes] = await Promise.all([
        fetch('/admin/users', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/admin/groups', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/admin/features', { headers: { Authorization: `Bearer ${token}` } })
      ]);

      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(usersData);
      }

      if (groupsRes.ok) {
        const groupsData = await groupsRes.json();
        setGroups(groupsData);
      }

      if (featuresRes.ok) {
        const featuresData = await featuresRes.json();
        setFeatures(featuresData);
        setAvailableFeatures(featuresData);
      }
    } catch (error) {
      console.error('데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('ko-KR');
  };

  const deleteUser = async (userId: string) => {
    if (!confirm('정말로 이 사용자를 삭제하시겠습니까?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('사용자가 성공적으로 삭제되었습니다.');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`사용자 삭제 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('사용자 삭제 중 오류:', error);
      alert('사용자 삭제 중 오류가 발생했습니다.');
    }
  };

  // 사용자 편집 모달 열기
  const openUserModal = async (user: User) => {
    console.log('사용자 모달 열기:', user);
    console.log('사용자 그룹 정보:', user.group);
    console.log('사용자 bio:', user.bio);
    
    try {
      // 사용자 상세 정보를 API로 가져오기
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/users/${user.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const userDetail = await response.json();
        console.log('API에서 가져온 사용자 상세 정보:', userDetail);
        
        setSelectedUser(userDetail);
        setEditedUserInfo({
          real_name: userDetail.real_name || '',
          display_name: userDetail.display_name || '',
          phone_number: userDetail.phone_number || '',
          department: userDetail.department || '',
          position: userDetail.position || '',
          bio: userDetail.bio || ''
        });
        setSelectedGroupId(userDetail.group?.id || null);
        
        console.log('API에서 가져온 그룹 ID:', userDetail.group?.id || null);
        console.log('API에서 가져온 bio:', userDetail.bio);
      } else {
        console.error('사용자 상세 정보 로드 실패');
        // 기존 정보로 폴백
        setSelectedUser(user);
        setEditedUserInfo({
          real_name: user.real_name || '',
          display_name: user.display_name || '',
          phone_number: user.phone_number || '',
          department: user.department || '',
          position: user.position || '',
          bio: user.bio || ''
        });
        setSelectedGroupId(user.group?.id || null);
      }
    } catch (error) {
      console.error('사용자 상세 정보 로드 중 오류:', error);
      // 기존 정보로 폴백
      setSelectedUser(user);
      setEditedUserInfo({
        real_name: user.real_name || '',
        display_name: user.display_name || '',
        phone_number: user.phone_number || '',
        department: user.department || '',
        position: user.position || '',
        bio: user.bio || ''
      });
      setSelectedGroupId(user.group?.id || null);
    }
    
    setIsEditingUserInfo(false);
    setShowUserModal(true);
  };

  // 사용자 정보 저장
  const saveUserInfo = async () => {
    if (!selectedUser) return;

    try {
      const token = localStorage.getItem('token');
      const requestData = {
        ...editedUserInfo,
        group_id: selectedGroupId || null
      };
      
      console.log('사용자 정보 업데이트 요청:', requestData);
      
      const response = await fetch(`/admin/users/${selectedUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('사용자 정보 업데이트 결과:', result);
        alert('사용자 정보가 성공적으로 수정되었습니다.');
        setShowUserModal(false);
        fetchData();
      } else {
        const errorData = await response.json();
        console.error('사용자 정보 수정 실패:', errorData);
        alert(errorData.detail || '사용자 정보 수정 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('사용자 정보 수정 실패:', error);
      alert('사용자 정보 수정 중 오류가 발생했습니다.');
    }
  };

  // 사용자 승인/활성화
  const updateUserStatus = async (userId: string, status: string, isActive: boolean) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/users/${userId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          approval_status: status,
          is_active: isActive
        }),
      });

      if (response.ok) {
        alert('사용자 상태가 성공적으로 변경되었습니다.');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(errorData.detail || '사용자 상태 변경 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('사용자 상태 변경 실패:', error);
      alert('사용자 상태 변경 중 오류가 발생했습니다.');
    }
  };

  // CSV Export 기능
  const exportUsersToCSV = () => {
    const headers = ['ID', '이름', '표시명', '이메일', '연락처', '부서', '직책', '상태', '그룹', '생성일'];
    const csvData = users.map(user => [
      user.id,
      user.real_name,
      user.display_name || '',
      user.email,
      user.phone_number || '',
      user.department || '',
      user.position || '',
      user.approval_status,
      user.group?.name || '',
      formatDate(user.created_at)
    ]);

    const csvContent = [headers, ...csvData]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `users_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  // CSV 일괄 업로드
  const handleBulkImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const csv = e.target?.result as string;
        const lines = csv.split('\n');
        const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
        
        const userData = [];
        for (let i = 1; i < lines.length; i++) {
          if (lines[i].trim()) {
            const values = lines[i].split(',').map(v => v.replace(/"/g, '').trim());
            const user: any = {};
            headers.forEach((header, index) => {
              user[header] = values[index] || '';
            });
            userData.push(user);
          }
        }

        const token = localStorage.getItem('token');
        const response = await fetch('/admin/users/bulk-import', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ users: userData }),
        });

        if (response.ok) {
          alert('사용자가 성공적으로 일괄 생성되었습니다.');
          fetchData();
        } else {
          const errorData = await response.json();
          alert(errorData.detail || '일괄 생성 중 오류가 발생했습니다.');
        }
      } catch (error) {
        console.error('CSV 파싱 오류:', error);
        alert('CSV 파일 형식이 올바르지 않습니다.');
      }
    };
    reader.readAsText(file);
  };

  // 기능 관리 함수들
  const openFeatureModal = (feature: Feature | null = null) => {
    if (feature) {
      setSelectedFeature(feature);
      setEditedFeatureInfo({
        name: feature.name,
        display_name: feature.display_name,
        description: feature.description,
        category: feature.category,
        icon: feature.icon,
        url_path: feature.url_path,
        is_active: feature.is_active,
        requires_approval: feature.requires_approval,
        is_external: feature.is_external || false,
        open_in_new_tab: feature.open_in_new_tab || false
      });
    } else {
      setSelectedFeature(null);
      setEditedFeatureInfo({
        name: '',
        display_name: '',
        description: '',
        category: '분석 도구',
        icon: '📊',
        url_path: '',
        is_active: true,
        requires_approval: false,
        is_external: false,
        open_in_new_tab: false
      });
    }
    setShowFeatureModal(true);
    setIsEditingFeature(false);
  };

  const saveFeature = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = selectedFeature 
        ? `/admin/features/${selectedFeature.id}`
        : '/admin/features';
      const method = selectedFeature ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(editedFeatureInfo),
      });

      if (response.ok) {
        alert(`기능이 성공적으로 ${selectedFeature ? '수정' : '생성'}되었습니다.`);
        setShowFeatureModal(false);
        fetchData();
      } else {
        const errorData = await response.json();
        alert(errorData.detail || '기능 저장 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('기능 저장 실패:', error);
      alert('기능 저장 중 오류가 발생했습니다.');
    }
  };

  const deleteFeature = async (featureId: number) => {
    if (!confirm('정말로 이 기능을 삭제하시겠습니까?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/features/${featureId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        alert('기능이 성공적으로 삭제되었습니다.');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(errorData.detail || '기능 삭제 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('기능 삭제 실패:', error);
      alert('기능 삭제 중 오류가 발생했습니다.');
    }
  };

  // 그룹 관리 함수들
  const openGroupModal = async (group: Group | null = null) => {
    if (group) {
      try {
        // 그룹 상세 정보를 API로 가져오기
        const token = localStorage.getItem('token');
        const response = await fetch(`/admin/groups/${group.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.ok) {
          const groupDetail = await response.json();
          setSelectedGroup(groupDetail);
          setEditedGroupInfo({
            name: groupDetail.name,
            description: groupDetail.description || ''
          });
          setSelectedGroupFeatures(groupDetail.features?.map((f: Feature) => f.id) || []);
        } else {
          console.error('그룹 상세 정보 로드 실패');
          setSelectedGroup(group);
          setEditedGroupInfo({
            name: group.name,
            description: group.description || ''
          });
          setSelectedGroupFeatures(group.features?.map((f: Feature) => f.id) || []);
        }
      } catch (error) {
        console.error('그룹 상세 정보 로드 중 오류:', error);
        setSelectedGroup(group);
        setEditedGroupInfo({
          name: group.name,
          description: group.description || ''
        });
                  setSelectedGroupFeatures(group.features?.map((f: Feature) => f.id) || []);
      }
    } else {
      setSelectedGroup(null);
      setEditedGroupInfo({ name: '', description: '' });
      setSelectedGroupFeatures([]);
    }
    setIsEditingGroup(false);
    setShowGroupModal(true);
  };

  const saveGroup = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (selectedGroup) {
        // 기존 그룹 수정
        const response = await fetch(`/admin/groups/${selectedGroup.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(editedGroupInfo),
        });

        if (response.ok) {
          // 그룹 기능 업데이트
          await updateGroupFeatures(selectedGroup.id);
          alert('그룹이 성공적으로 수정되었습니다.');
        } else {
          const errorData = await response.json();
          alert(errorData.detail || '그룹 수정 중 오류가 발생했습니다.');
          return;
        }
      } else {
        // 새 그룹 생성
        const response = await fetch('/admin/groups', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(editedGroupInfo),
        });

        if (response.ok) {
          const newGroup = await response.json();
          // 새 그룹에 기능 할당
          await updateGroupFeatures(newGroup.id);
          alert('그룹이 성공적으로 생성되었습니다.');
        } else {
          const errorData = await response.json();
          alert(errorData.detail || '그룹 생성 중 오류가 발생했습니다.');
          return;
        }
      }

      setShowGroupModal(false);
      fetchData();
    } catch (error) {
      console.error('그룹 저장 실패:', error);
      alert('그룹 저장 중 오류가 발생했습니다.');
    }
  };

  const updateGroupFeatures = async (groupId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/admin/groups/features', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          group_id: groupId,
          feature_ids: selectedGroupFeatures
        }),
      });

      if (!response.ok) {
        throw new Error('그룹 기능 업데이트 실패');
      }
    } catch (error) {
      console.error('그룹 기능 업데이트 실패:', error);
      throw error;
    }
  };

  const deleteGroup = async (groupId: number) => {
    if (!confirm('정말로 이 그룹을 삭제하시겠습니까?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/groups/${groupId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        alert('그룹이 성공적으로 삭제되었습니다.');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(errorData.detail || '그룹 삭제 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('그룹 삭제 실패:', error);
      alert('그룹 삭제 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* 배경 애니메이션 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-32 w-96 h-96 bg-gradient-to-r from-blue-400/20 to-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-32 -left-32 w-80 h-80 bg-gradient-to-r from-purple-400/20 to-pink-500/20 rounded-full blur-3xl animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-32 right-1/3 w-72 h-72 bg-gradient-to-r from-pink-400/20 to-blue-500/20 rounded-full blur-3xl animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10 flex min-h-screen">
        {/* 사이드바 */}
        <div className="w-64 bg-white/80 backdrop-blur-md shadow-2xl border-r border-white/20">
          <div className="p-6">
            {/* 로고 및 타이틀 */}
            <div className="flex items-center space-x-3 mb-8">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white text-xl font-bold">A</span>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  관리자 도구
                </h1>
                <p className="text-xs text-gray-500">Admin Console</p>
              </div>
            </div>

            {/* 네비게이션 메뉴 */}
            <nav className="space-y-2">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                  activeTab === 'dashboard'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-white/60 hover:shadow-md'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="font-medium">대시보드</span>
              </button>

              <button
                onClick={() => setActiveTab('users')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                  activeTab === 'users'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-white/60 hover:shadow-md'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
                <span className="font-medium">사용자 관리</span>
              </button>

              <button
                onClick={() => setActiveTab('features')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                  activeTab === 'features'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-white/60 hover:shadow-md'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
                <span className="font-medium">기능 관리</span>
              </button>

              <button
                onClick={() => setActiveTab('groups')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                  activeTab === 'groups'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-white/60 hover:shadow-md'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <span className="font-medium">그룹 관리</span>
              </button>
            </nav>

            {/* Main Page 돌아가기 버튼 */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <button
                onClick={() => navigate('/main')}
                className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 group"
              >
                <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span className="font-medium">Main Page 돌아가기</span>
              </button>
            </div>
          </div>
        </div>

        {/* 메인 콘텐츠 */}
        <div className="flex-1 p-8">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-spin"></div>
                <div className="absolute top-2 left-2 w-12 h-12 bg-white rounded-full"></div>
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              {/* 대시보드 탭 */}
              {activeTab === 'dashboard' && (
                <div className="space-y-8">
                  <div className="text-center">
                    <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
                      관리자 대시보드
                    </h2>
                    <p className="text-gray-600 text-lg">시스템 현황을 한눈에 확인하세요</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                          </svg>
                        </div>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">총 사용자 수</h3>
                      <p className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-blue-600 bg-clip-text text-transparent">{users.length}</p>
                    </div>
                    
                    <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">활성 사용자</h3>
                      <p className="text-4xl font-bold bg-gradient-to-r from-green-500 to-green-600 bg-clip-text text-transparent">
                        {users.filter(u => u.is_active).length}
                      </p>
                    </div>
                    
                    <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center">
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">승인 대기</h3>
                      <p className="text-4xl font-bold bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
                        {users.filter(u => u.approval_status === 'pending').length}
                      </p>
                    </div>
                    
                    <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
                          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                          </svg>
                        </div>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">관리자</h3>
                      <p className="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-600 bg-clip-text text-transparent">
                        {users.filter(u => u.is_admin).length}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* 사용자 관리 탭 */}
              {activeTab === 'users' && (
                <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
                  <div className="px-8 py-6 border-b border-white/20 bg-gradient-to-r from-blue-50 to-purple-50 flex justify-between items-center">
                    <div>
                      <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">사용자 목록</h3>
                      <p className="text-gray-600 mt-1">시스템 사용자를 관리합니다</p>
                    </div>
                    <div className="flex space-x-3">
                      <button
                        onClick={exportUsersToCSV}
                        className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>CSV 내보내기</span>
                      </button>
                      <label className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200 cursor-pointer flex items-center space-x-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <span>일괄 업로드</span>
                        <input
                          type="file"
                          accept=".csv,.xlsx,.xls"
                          onChange={handleBulkImport}
                          className="hidden"
                        />
                      </label>
                    </div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            사용자
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            부서/직책
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            상태
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            그룹
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            최근로그인
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            액션
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {users.map((user) => (
                          <tr key={user.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <div>
                                  <div className="text-sm font-medium text-gray-900">
                                    {user.display_name || user.real_name}
                                    {user.is_admin && (
                                      <span className="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                                        관리자
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-sm text-gray-500">{user.email}</div>
                                  <div className="text-xs text-gray-400">{user.phone_number}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{user.department || '-'}</div>
                              <div className="text-sm text-gray-500">{user.position || '-'}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex flex-col space-y-1">
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  user.approval_status === 'approved' ? 'bg-green-100 text-green-800' :
                                  user.approval_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {user.approval_status === 'approved' ? '승인됨' :
                                   user.approval_status === 'pending' ? '승인대기' : '거절됨'}
                                </span>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  user.is_active ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {user.is_active ? '활성' : '비활성'}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {user.group ? (
                                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                                  {user.group.name}
                                </span>
                              ) : (
                                <span className="text-sm text-gray-500">-</span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{formatDate(user.last_login_at)}</div>
                              <div className="text-xs text-gray-500">로그인 {user.login_count || 0}회</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => openUserModal(user)}
                                  className="text-blue-600 hover:text-blue-900 font-medium"
                                >
                                  편집
                                </button>
                                <button
                                  onClick={() => deleteUser(user.id)}
                                  className="text-red-600 hover:text-red-900 font-medium"
                                >
                                  삭제
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* 기능관리 탭 */}
              {activeTab === 'features' && (
                <div className="space-y-6">
                  {/* 기능 카드 미리보기 */}
                  <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
                    <div className="px-8 py-6 border-b border-white/20 bg-gradient-to-r from-blue-50 to-purple-50 flex justify-between items-center">
                      <div>
                        <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Main페이지 미리보기</h3>
                        <p className="text-gray-600 mt-1">현재 등록된 기능들이 Main페이지에서 어떻게 보일지 미리 확인합니다</p>
                      </div>
                      <button
                        onClick={() => setShowPreview(!showPreview)}
                        className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all duration-200 ${
                          showPreview 
                            ? 'bg-gray-500 text-white hover:bg-gray-600' 
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                      >
                        {showPreview ? '미리보기 숨기기' : '미리보기 보기'}
                      </button>
                    </div>

                    {showPreview && (
                      <div className="p-8">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                          {features
                            .filter(feature => feature.is_active)
                            .map((feature) => (
                            <div
                              key={feature.id}
                              className="group bg-white/60 backdrop-blur-sm border border-white/20 rounded-2xl p-6 hover:shadow-xl hover:bg-white/80 transition-all duration-300 cursor-pointer"
                            >
                              <div className="flex items-center justify-between mb-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl flex items-center justify-center">
                                  <span className="text-2xl" style={{ fontFamily: 'Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, sans-serif' }}>
                                    {feature.icon}
                                  </span>
                                </div>
                                <div className="flex items-center space-x-2">
                                  {feature.is_external && (
                                    <span className="w-2 h-2 bg-orange-400 rounded-full" title="외부 링크"></span>
                                  )}
                                  {feature.requires_approval && (
                                    <span className="w-2 h-2 bg-yellow-400 rounded-full" title="승인 필요"></span>
                                  )}
                                </div>
                              </div>
                              <h4 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                                {feature.display_name}
                              </h4>
                              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                                {feature.description}
                              </p>
                              <div className="flex items-center justify-between">
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
                                  {feature.category}
                                </span>
                                <svg className="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 기능 목록 */}
                  <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
                    <div className="px-8 py-6 border-b border-white/20 bg-gradient-to-r from-blue-50 to-purple-50 flex justify-between items-center">
                      <div>
                        <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">기능 목록</h3>
                        <p className="text-gray-600 mt-1">등록된 모든 기능을 관리합니다</p>
                      </div>
                      <button
                        onClick={() => openFeatureModal()}
                        className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span>기능 추가</span>
                      </button>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              기능
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              카테고리
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              URL 정보
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              상태
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              설정
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              액션
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {features.map((feature) => (
                            <tr key={feature.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                  <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center mr-4">
                                    <span className="text-lg" style={{ fontFamily: 'Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, sans-serif' }}>
                                      {feature.icon}
                                    </span>
                                  </div>
                                  <div>
                                    <div className="text-sm font-medium text-gray-900">
                                      {feature.display_name}
                                    </div>
                                    <div className="text-sm text-gray-500">{feature.name}</div>
                                    <div className="text-xs text-gray-400 mt-1 max-w-xs truncate">
                                      {feature.description}
                                    </div>
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                                  {feature.category}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900">
                                  <div className="flex items-center space-x-2">
                                    {feature.is_external ? (
                                      <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                                        외부 링크
                                      </span>
                                    ) : (
                                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                        내부 페이지
                                      </span>
                                    )}
                                    {feature.open_in_new_tab && (
                                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                        새 탭
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-xs text-gray-500 mt-1">
                                    {feature.url_path}
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  feature.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {feature.is_active ? '활성' : '비활성'}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex flex-col space-y-1">
                                  {feature.requires_approval && (
                                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                                      승인 필요
                                    </span>
                                  )}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => openFeatureModal(feature)}
                                    className="text-blue-600 hover:text-blue-900 font-medium"
                                  >
                                    편집
                                  </button>
                                  <button
                                    onClick={() => deleteFeature(feature.id)}
                                    className="text-red-600 hover:text-red-900 font-medium"
                                  >
                                    삭제
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* 그룹 관리 탭 */}
              {activeTab === 'groups' && (
                <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
                  <div className="px-8 py-6 border-b border-white/20 bg-gradient-to-r from-blue-50 to-purple-50 flex justify-between items-center">
                    <div>
                      <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">그룹 목록</h3>
                      <p className="text-gray-600 mt-1">사용자 그룹과 권한을 관리합니다</p>
                    </div>
                    <button
                      onClick={() => openGroupModal()}
                      className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      <span>새 그룹 생성</span>
                    </button>
                  </div>
                  
                  <div className="p-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                      {groups.map((group) => (
                        <div key={group.id} className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:shadow-xl transition-all duration-300">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-500 rounded-xl flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                              </div>
                              <div>
                                <h4 className="text-lg font-bold text-gray-900">{group.name}</h4>
                                <p className="text-sm text-gray-600">{group.description || '설명 없음'}</p>
                              </div>
                            </div>
                            <div className="flex space-x-1">
                              <button
                                onClick={() => openGroupModal(group)}
                                className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                                title="편집"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                              </button>
                              <button
                                onClick={() => deleteGroup(group.id)}
                                className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
                                title="삭제"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            </div>
                          </div>

                          {/* 그룹 통계 */}
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div className="bg-blue-50 rounded-lg p-3 text-center">
                              <div className="text-2xl font-bold text-blue-600">
                                {group.users_count || 0}
                              </div>
                              <div className="text-xs text-blue-600">소속 사용자</div>
                            </div>
                            <div className="bg-purple-50 rounded-lg p-3 text-center">
                              <div className="text-2xl font-bold text-purple-600">
                                {group.features?.length || 0}
                              </div>
                              <div className="text-xs text-purple-600">사용 가능 기능</div>
                            </div>
                          </div>

                          {/* 기능 미리보기 */}
                          {group.features && group.features.length > 0 && (
                            <div className="mb-4">
                              <h5 className="text-sm font-medium text-gray-700 mb-2">사용 가능한 기능</h5>
                              <div className="flex flex-wrap gap-1">
                                {group.features.slice(0, 3).map((feature) => (
                                  <span key={feature.id} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                                    {feature.icon} {feature.display_name}
                                  </span>
                                ))}
                                {group.features.length > 3 && (
                                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                    +{group.features.length - 3}개 더
                                  </span>
                                )}
                              </div>
                            </div>
                          )}

                          {/* 그룹 정보 */}
                          <div className="text-xs text-gray-500 space-y-1">
                            <div className="flex justify-between">
                              <span>생성일:</span>
                              <span>{formatDate(group.created_at)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>생성자:</span>
                              <span>{group.created_by || '시스템'}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 사용자 편집 모달 */}
      {showUserModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-8">
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    사용자 정보 편집
                  </h3>
                  <p className="text-gray-600 mt-1">사용자의 정보를 수정하고 권한을 관리합니다</p>
                </div>
                <button
                  onClick={() => setShowUserModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* 기본 정보 섹션 */}
                <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    기본 정보
                  </h4>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">실명</label>
                      <input
                        type="text"
                        value={editedUserInfo.real_name}
                        onChange={(e) => setEditedUserInfo({...editedUserInfo, real_name: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={!isEditingUserInfo}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">표시명</label>
                      <input
                        type="text"
                        value={editedUserInfo.display_name}
                        onChange={(e) => setEditedUserInfo({...editedUserInfo, display_name: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={!isEditingUserInfo}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">연락처</label>
                      <input
                        type="tel"
                        value={editedUserInfo.phone_number}
                        onChange={(e) => setEditedUserInfo({...editedUserInfo, phone_number: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={!isEditingUserInfo}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">부서</label>
                      <input
                        type="text"
                        value={editedUserInfo.department}
                        onChange={(e) => setEditedUserInfo({...editedUserInfo, department: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={!isEditingUserInfo}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">직책</label>
                      <input
                        type="text"
                        value={editedUserInfo.position}
                        onChange={(e) => setEditedUserInfo({...editedUserInfo, position: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={!isEditingUserInfo}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">소개</label>
                      <textarea
                        value={editedUserInfo.bio}
                        onChange={(e) => setEditedUserInfo({...editedUserInfo, bio: e.target.value})}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        disabled={!isEditingUserInfo}
                      />
                    </div>
                  </div>
                </div>

                {/* 계정 상태 및 그룹 섹션 */}
                <div className="space-y-6">
                  {/* 계정 상태 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      계정 상태
                    </h4>
                    
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm font-medium text-gray-700">승인 상태</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          selectedUser.approval_status === 'approved' ? 'bg-green-100 text-green-800' :
                          selectedUser.approval_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {selectedUser.approval_status === 'approved' ? '승인됨' :
                           selectedUser.approval_status === 'pending' ? '승인대기' : '거절됨'}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm font-medium text-gray-700">활성 상태</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          selectedUser.is_active ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedUser.is_active ? '활성' : '비활성'}
                        </span>
                      </div>
                      
                      <div className="flex space-x-2">
                        {selectedUser.approval_status !== 'approved' && (
                          <button
                            onClick={() => updateUserStatus(selectedUser.id, 'approved', true)}
                            className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                          >
                            승인 & 활성화
                          </button>
                        )}
                        {selectedUser.approval_status === 'approved' && (
                          <button
                            onClick={() => updateUserStatus(selectedUser.id, 'approved', !selectedUser.is_active)}
                            className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors ${
                              selectedUser.is_active 
                                ? 'bg-orange-600 text-white hover:bg-orange-700' 
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                            }`}
                          >
                            {selectedUser.is_active ? '비활성화' : '활성화'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* 그룹 할당 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      그룹 할당
                    </h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">소속 그룹</label>
                      <select
                        value={selectedGroupId || ''}
                        onChange={(e) => {
                          const newGroupId = e.target.value ? Number(e.target.value) : null;
                          console.log('그룹 선택 변경:', newGroupId);
                          setSelectedGroupId(newGroupId);
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={!isEditingUserInfo}
                      >
                        <option value="">그룹 없음</option>
                        {groups.map((group) => (
                          <option key={group.id} value={group.id}>
                            {group.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* 계정 정보 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      계정 정보
                    </h4>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">이메일:</span>
                        <span className="text-gray-900">{selectedUser.email}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">가입일:</span>
                        <span className="text-gray-900">{formatDate(selectedUser.created_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">최근 로그인:</span>
                        <span className="text-gray-900">{formatDate(selectedUser.last_login_at) || '없음'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">로그인 횟수:</span>
                        <span className="text-gray-900">{selectedUser.login_count || 0}회</span>
                      </div>
                      {selectedUser.is_admin && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">권한:</span>
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">관리자</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setIsEditingUserInfo(!isEditingUserInfo)}
                  className={`px-6 py-3 text-sm font-semibold rounded-xl transition-all duration-200 ${
                    isEditingUserInfo
                      ? 'bg-gray-500 text-white hover:bg-gray-600'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {isEditingUserInfo ? '편집 취소' : '정보 편집'}
                </button>
                
                <div className="flex space-x-3">
                  <button
                    onClick={() => setShowUserModal(false)}
                    className="px-6 py-3 bg-gray-200 text-gray-800 text-sm font-semibold rounded-xl hover:bg-gray-300 transition-all duration-200"
                  >
                    닫기
                  </button>
                  {isEditingUserInfo && (
                    <button
                      onClick={saveUserInfo}
                      className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                    >
                      저장
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 기능 편집/추가 모달 */}
      {showFeatureModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-8">
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {selectedFeature ? '기능 편집' : '새 기능 추가'}
                  </h3>
                  <p className="text-gray-600 mt-1">기능의 정보를 설정하고 MainPage에 표시될 내용을 구성합니다</p>
                </div>
                <button
                  onClick={() => setShowFeatureModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* 기본 정보 섹션 */}
                <div className="space-y-6">
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      기본 정보
                    </h4>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">기능 이름 (시스템용)</label>
                        <input
                          type="text"
                          value={editedFeatureInfo.name}
                          onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, name: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="예: data_analysis"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">표시될 이름</label>
                        <input
                          type="text"
                          value={editedFeatureInfo.display_name}
                          onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, display_name: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="예: 데이터 분석"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">설명</label>
                        <textarea
                          value={editedFeatureInfo.description}
                          onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, description: e.target.value})}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                          placeholder="기능에 대한 간단한 설명을 입력하세요"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
                        <select
                          value={editedFeatureInfo.category}
                          onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, category: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="분석 도구">분석 도구</option>
                          <option value="업무 관리">업무 관리</option>
                          <option value="리포트">리포트</option>
                          <option value="설정">설정</option>
                          <option value="사용자 도구">사용자 도구</option>
                          <option value="기타">기타</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">아이콘 (이모지)</label>
                        <div className="flex items-center space-x-3">
                          <input
                            type="text"
                            value={editedFeatureInfo.icon}
                            onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, icon: e.target.value})}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="📊"
                          />
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-500 rounded-xl flex items-center justify-center text-2xl">
                            {editedFeatureInfo.icon || '🔧'}
                          </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">이모지를 입력하거나 복사해서 붙여넣으세요</p>
                      </div>
                    </div>
                  </div>

                  {/* URL 설정 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      URL 설정
                    </h4>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">URL 경로</label>
                        <input
                          type="text"
                          value={editedFeatureInfo.url_path}
                          onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, url_path: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="/dashboard 또는 https://example.com"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="text-sm font-medium text-gray-700">외부 링크</span>
                          <p className="text-xs text-gray-500">외부 웹사이트로 연결되는 링크인 경우 체크</p>
                        </div>
                        <label className="flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={editedFeatureInfo.is_external}
                            onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, is_external: e.target.checked})}
                            className="sr-only"
                          />
                          <div className={`relative w-11 h-6 rounded-full transition-colors ${
                            editedFeatureInfo.is_external ? 'bg-blue-600' : 'bg-gray-300'
                          }`}>
                            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                              editedFeatureInfo.is_external ? 'translate-x-5' : 'translate-x-0'
                            }`}></div>
                          </div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="text-sm font-medium text-gray-700">새 탭에서 열기</span>
                          <p className="text-xs text-gray-500">클릭 시 새 탭에서 열리도록 설정</p>
                        </div>
                        <label className="flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={editedFeatureInfo.open_in_new_tab}
                            onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, open_in_new_tab: e.target.checked})}
                            className="sr-only"
                          />
                          <div className={`relative w-11 h-6 rounded-full transition-colors ${
                            editedFeatureInfo.open_in_new_tab ? 'bg-blue-600' : 'bg-gray-300'
                          }`}>
                            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                              editedFeatureInfo.open_in_new_tab ? 'translate-x-5' : 'translate-x-0'
                            }`}></div>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 설정 및 미리보기 섹션 */}
                <div className="space-y-6">
                  {/* 기능 설정 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      기능 설정
                    </h4>
                    
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="text-sm font-medium text-gray-700">활성 상태</span>
                          <p className="text-xs text-gray-500">활성화된 기능만 메인페이지에 표시됩니다</p>
                        </div>
                        <label className="flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={editedFeatureInfo.is_active}
                            onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, is_active: e.target.checked})}
                            className="sr-only"
                          />
                          <div className={`relative w-11 h-6 rounded-full transition-colors ${
                            editedFeatureInfo.is_active ? 'bg-green-600' : 'bg-gray-300'
                          }`}>
                            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                              editedFeatureInfo.is_active ? 'translate-x-5' : 'translate-x-0'
                            }`}></div>
                          </div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="text-sm font-medium text-gray-700">승인 필요</span>
                          <p className="text-xs text-gray-500">사용자가 이 기능을 사용하려면 관리자 승인이 필요합니다</p>
                        </div>
                        <label className="flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={editedFeatureInfo.requires_approval}
                            onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, requires_approval: e.target.checked})}
                            className="sr-only"
                          />
                          <div className={`relative w-11 h-6 rounded-full transition-colors ${
                            editedFeatureInfo.requires_approval ? 'bg-yellow-600' : 'bg-gray-300'
                          }`}>
                            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                              editedFeatureInfo.requires_approval ? 'translate-x-5' : 'translate-x-0'
                            }`}></div>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* 카드 미리보기 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      카드 미리보기
                    </h4>
                    
                    <div className="border-2 border-dashed border-gray-300 rounded-xl p-6">
                      <div className="bg-white/60 backdrop-blur-sm border border-white/20 rounded-2xl p-6 hover:shadow-xl transition-all duration-300">
                        <div className="flex items-center justify-between mb-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-500 rounded-xl flex items-center justify-center text-2xl">
                            {editedFeatureInfo.icon || '🔧'}
                          </div>
                          <div className="flex items-center space-x-2">
                            {editedFeatureInfo.is_external && (
                              <span className="w-2 h-2 bg-orange-400 rounded-full" title="외부 링크"></span>
                            )}
                            {editedFeatureInfo.requires_approval && (
                              <span className="w-2 h-2 bg-yellow-400 rounded-full" title="승인 필요"></span>
                            )}
                          </div>
                        </div>
                        <h4 className="text-lg font-bold text-gray-900 mb-2">
                          {editedFeatureInfo.display_name || '기능 이름'}
                        </h4>
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {editedFeatureInfo.description || '기능 설명이 여기에 표시됩니다.'}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
                            {editedFeatureInfo.category}
                          </span>
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  * 저장 후 변경사항이 Main페이지에 반영됩니다
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={() => setShowFeatureModal(false)}
                    className="px-6 py-3 bg-gray-200 text-gray-800 text-sm font-semibold rounded-xl hover:bg-gray-300 transition-all duration-200"
                  >
                    취소
                  </button>
                  <button
                    onClick={saveFeature}
                    className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                  >
                    {selectedFeature ? '수정 완료' : '기능 추가'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 그룹 편집/생성 모달 */}
      {showGroupModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 w-full max-w-6xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-8">
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {selectedGroup ? '그룹 편집' : '새 그룹 생성'}
                  </h3>
                  <p className="text-gray-600 mt-1">그룹 정보를 설정하고 기능 권한을 관리합니다</p>
                </div>
                <button
                  onClick={() => setShowGroupModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* 그룹 기본 정보 */}
                <div className="space-y-6">
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      그룹 정보
                    </h4>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">그룹 이름</label>
                        <input
                          type="text"
                          value={editedGroupInfo.name}
                          onChange={(e) => setEditedGroupInfo({...editedGroupInfo, name: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="예: 데이터 분석팀"
                          disabled={!isEditingGroup}
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">그룹 설명</label>
                        <textarea
                          value={editedGroupInfo.description}
                          onChange={(e) => setEditedGroupInfo({...editedGroupInfo, description: e.target.value})}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                          placeholder="그룹에 대한 설명을 입력하세요"
                          disabled={!isEditingGroup}
                        />
                      </div>

                      <div className="flex justify-between items-center">
                        <button
                          onClick={() => setIsEditingGroup(!isEditingGroup)}
                          className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                            isEditingGroup
                              ? 'bg-gray-500 text-white hover:bg-gray-600'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                        >
                          {isEditingGroup ? '편집 취소' : '정보 편집'}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* 기능 권한 관리 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                      기능 권한 설정
                    </h4>
                    
                    <div className="max-h-80 overflow-y-auto space-y-3">
                      {availableFeatures.map((feature) => (
                        <div key={feature.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-lg flex items-center justify-center text-sm">
                              {feature.icon}
                            </div>
                            <div>
                              <div className="text-sm font-medium text-gray-900">{feature.display_name}</div>
                              <div className="text-xs text-gray-500">{feature.description}</div>
                              <div className="flex items-center space-x-2 mt-1">
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                                  {feature.category}
                                </span>
                                {feature.is_external && (
                                  <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                                    외부링크
                                  </span>
                                )}
                                {feature.requires_approval && (
                                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                                    승인필요
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <label className="flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={selectedGroupFeatures.includes(feature.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedGroupFeatures([...selectedGroupFeatures, feature.id]);
                                } else {
                                  setSelectedGroupFeatures(selectedGroupFeatures.filter(id => id !== feature.id));
                                }
                              }}
                              className="sr-only"
                            />
                            <div className={`relative w-10 h-6 rounded-full transition-colors ${
                              selectedGroupFeatures.includes(feature.id) ? 'bg-blue-600' : 'bg-gray-300'
                            }`}>
                              <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                                selectedGroupFeatures.includes(feature.id) ? 'translate-x-4' : 'translate-x-0'
                              }`}></div>
                            </div>
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 그룹 정보 및 소속 사용자 */}
                <div className="space-y-6">
                  {/* 그룹 통계 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      그룹 통계
                    </h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-blue-50 rounded-lg p-4 text-center">
                        <div className="text-3xl font-bold text-blue-600">
                          {selectedGroup?.users_count || 0}
                        </div>
                        <div className="text-sm text-blue-600 mt-1">소속 사용자</div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-4 text-center">
                        <div className="text-3xl font-bold text-purple-600">
                          {selectedGroupFeatures.length}
                        </div>
                        <div className="text-sm text-purple-600 mt-1">사용 가능 기능</div>
                      </div>
                    </div>
                  </div>

                  {/* 소속 사용자 목록 */}
                  {selectedGroup && (
                    <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <svg className="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        소속 사용자 ({selectedGroup.users_count || 0}명)
                      </h4>
                      
                      <div className="max-h-80 overflow-y-auto">
                        {selectedGroup.users && selectedGroup.users.length > 0 ? (
                          <div className="space-y-4">
                            {selectedGroup.users.map((user) => (
                              <div key={user.id} className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
                                <div className="flex items-start justify-between">
                                  {/* 사용자 기본 정보 */}
                                  <div className="flex items-start space-x-4">
                                    <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold shadow-sm">
                                      {(user.display_name || user.real_name).charAt(0)}
                                    </div>
                                    <div className="flex-1">
                                      <div className="flex items-center space-x-2 mb-2">
                                        <h5 className="text-base font-semibold text-gray-900">
                                          {user.display_name || user.real_name}
                                        </h5>
                                        {user.is_admin && (
                                          <span className="px-2 py-1 text-xs bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 rounded-full font-medium">
                                            👑 관리자
                                          </span>
                                        )}
                                      </div>
                                      
                                      <div className="text-sm text-gray-600 mb-3">
                                        <div className="flex items-center space-x-1 mb-1">
                                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                                          </svg>
                                          <span>{user.email}</span>
                                        </div>
                                        {user.phone_number && (
                                          <div className="flex items-center space-x-1 mb-1">
                                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                            </svg>
                                            <span>{user.phone_number}</span>
                                          </div>
                                        )}
                                      </div>

                                      {/* 상태 배지들 */}
                                      <div className="flex flex-wrap gap-2 mb-3">
                                        {/* 활성 상태 */}
                                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                                          user.is_active 
                                            ? 'bg-green-100 text-green-800 border border-green-200' 
                                            : 'bg-gray-100 text-gray-800 border border-gray-200'
                                        }`}>
                                          <div className={`w-2 h-2 rounded-full mr-1.5 ${user.is_active ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                                          {user.is_active ? '🟢 활성' : '⚫ 비활성'}
                                        </span>

                                        {/* 인증 상태 */}
                                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                                          user.is_verified 
                                            ? 'bg-blue-100 text-blue-800 border border-blue-200' 
                                            : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                                        }`}>
                                          {user.is_verified ? '✅ 인증완료' : '⏳ 인증대기'}
                                        </span>

                                        {/* 승인 상태 */}
                                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                                          user.approval_status === 'approved' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                                          user.approval_status === 'pending' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                                          'bg-red-100 text-red-800 border border-red-200'
                                        }`}>
                                          {user.approval_status === 'approved' ? '✅ 승인됨' :
                                           user.approval_status === 'pending' ? '⏳ 승인대기' : '❌ 거절됨'}
                                        </span>

                                        {/* 역할 배지 */}
                                        {user.role_name && (
                                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-200">
                                            🎭 {user.role_name}
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  </div>

                                  {/* 부가 정보 */}
                                  <div className="text-right">
                                    <div className="bg-gray-50 rounded-lg p-3 min-w-[160px]">
                                      <div className="space-y-2 text-xs">
                                        <div className="flex justify-between">
                                          <span className="text-gray-600">부서:</span>
                                          <span className="font-medium text-gray-900">{user.department || '-'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="text-gray-600">직책:</span>
                                          <span className="font-medium text-gray-900">{user.position || '-'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="text-gray-600">로그인:</span>
                                          <span className="font-medium text-gray-900">{user.login_count}회</span>
                                        </div>
                                        <div className="border-t pt-2 mt-2">
                                          <span className="text-gray-600">최근 접속:</span>
                                          <div className="font-medium text-gray-900 mt-1">
                                            {user.last_login_at ? formatDate(user.last_login_at) : (
                                              <span className="text-gray-400">접속 기록 없음</span>
                                            )}
                                          </div>
                                        </div>
                                        <div className="border-t pt-2 mt-2">
                                          <span className="text-gray-600">가입일:</span>
                                          <div className="font-medium text-gray-900 mt-1">
                                            {formatDate(user.created_at)}
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-8 text-gray-500">
                            <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                            <p>아직 이 그룹에 소속된 사용자가 없습니다.</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* 권한 미리보기 */}
                  <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      선택된 기능 미리보기
                    </h4>
                    
                    {selectedGroupFeatures.length > 0 ? (
                      <div className="grid grid-cols-1 gap-3 max-h-64 overflow-y-auto">
                        {availableFeatures
                          .filter(feature => selectedGroupFeatures.includes(feature.id))
                          .map((feature) => (
                          <div key={feature.id} className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-lg flex items-center justify-center text-sm">
                              {feature.icon}
                            </div>
                            <div className="flex-1">
                              <div className="text-sm font-medium text-gray-900">{feature.display_name}</div>
                              <div className="text-xs text-gray-500">{feature.category}</div>
                            </div>
                            <div className="flex items-center space-x-1">
                              {feature.is_external && (
                                <span className="w-2 h-2 bg-orange-400 rounded-full" title="외부 링크"></span>
                              )}
                              {feature.requires_approval && (
                                <span className="w-2 h-2 bg-yellow-400 rounded-full" title="승인 필요"></span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                        </svg>
                        <p>기능을 선택하면 여기에 미리보기가 표시됩니다.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  * 권한 변경 후 저장하면 그룹 사용자들에게 즉시 적용됩니다
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={() => setShowGroupModal(false)}
                    className="px-6 py-3 bg-gray-200 text-gray-800 text-sm font-semibold rounded-xl hover:bg-gray-300 transition-all duration-200"
                  >
                    취소
                  </button>
                  <button
                    onClick={saveGroup}
                    className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                  >
                    {selectedGroup ? '그룹 수정' : '그룹 생성'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage; 