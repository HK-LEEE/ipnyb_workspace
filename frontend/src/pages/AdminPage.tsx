import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, Settings, Shield, Database, UserPlus, UserCheck, UserX, 
  Edit3, Trash2, Download, Upload, Search, RefreshCw, Plus,
  ChevronRight, AlertCircle, CheckCircle, XCircle, Clock,
  Eye, EyeOff, Key, Filter, Grid, List, MoreVertical
} from 'lucide-react';

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
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive' | 'pending'>('all');
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
  
  // 새로운 사용자 추가를 위한 상태
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [newUserInfo, setNewUserInfo] = useState({
    real_name: '',
    display_name: '',
    email: '',
    phone_number: '',
    department: '',
    position: '',
    bio: '',
    password: '',
    is_admin: false,
    group_id: null as number | null
  });

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

  const openUserModal = async (user: User) => {
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
    setShowUserModal(true);
  };

  const saveUserInfo = async () => {
    if (!selectedUser) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/users/${selectedUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...editedUserInfo,
          group_id: selectedGroupId
        })
      });

      if (response.ok) {
        alert('사용자 정보가 성공적으로 업데이트되었습니다.');
        setShowUserModal(false);
        setIsEditingUserInfo(false);
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`업데이트 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('사용자 정보 업데이트 중 오류:', error);
      alert('사용자 정보 업데이트 중 오류가 발생했습니다.');
    }
  };

  const updateUserStatus = async (userId: string, status: string, isActive: boolean) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/users/${userId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          approval_status: status,
          is_active: isActive
        })
      });

      if (response.ok) {
        alert('사용자 상태가 성공적으로 업데이트되었습니다.');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`상태 업데이트 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('사용자 상태 업데이트 중 오류:', error);
      alert('사용자 상태 업데이트 중 오류가 발생했습니다.');
    }
  };

  // ===========================================
  // 사용자 추가 기능
  // ===========================================

  const openAddUserModal = () => {
    setNewUserInfo({
      real_name: '',
      display_name: '',
      email: '',
      phone_number: '',
      department: '',
      position: '',
      bio: '',
      password: '',
      is_admin: false,
      group_id: null
    });
    setShowAddUserModal(true);
  };

  const createUser = async () => {
    if (!newUserInfo.real_name || !newUserInfo.email || !newUserInfo.password) {
      alert('실명, 이메일, 비밀번호는 필수 입력 항목입니다.');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          real_name: newUserInfo.real_name,
          display_name: newUserInfo.display_name,
          email: newUserInfo.email,
          password: newUserInfo.password,
          phone_number: newUserInfo.phone_number,
          department: newUserInfo.department,
          position: newUserInfo.position,
          bio: newUserInfo.bio
        })
      });

      if (response.ok) {
        const userData = await response.json();
        let successMessage = '사용자가 성공적으로 생성되었습니다.';
        
        // 관리자 권한 설정 (필요한 경우)
        if (newUserInfo.is_admin) {
          try {
            // 여기에 관리자 권한 설정 API 호출이 필요할 수 있습니다
            // 현재는 백엔드에서 해당 API가 없으므로 스킵
          } catch (error) {
            console.warn('관리자 권한 설정 실패:', error);
          }
        }
        
        // 그룹 설정 (필요한 경우)
        if (newUserInfo.group_id) {
          try {
            await fetch('/admin/users/group', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
              },
              body: JSON.stringify({
                user_id: userData.user?.id || userData.id,
                group_id: newUserInfo.group_id
              })
            });
            successMessage += ' 그룹도 설정되었습니다.';
          } catch (error) {
            console.warn('그룹 설정 실패:', error);
            successMessage += ' (그룹 설정은 실패했습니다)';
          }
        }
        
        alert(successMessage);
        setShowAddUserModal(false);
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`사용자 생성 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('사용자 생성 중 오류:', error);
      alert('사용자 생성 중 오류가 발생했습니다.');
    }
  };

  // ===========================================
  // 기능 관리 기능
  // ===========================================

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
      setIsEditingFeature(true);
    } else {
      setSelectedFeature(null);
      setEditedFeatureInfo({
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
      setIsEditingFeature(false);
    }
    setShowFeatureModal(true);
  };

  const saveFeature = async () => {
    if (!editedFeatureInfo.name || !editedFeatureInfo.display_name) {
      alert('기능명과 표시명은 필수 입력 항목입니다.');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const url = selectedFeature ? `/admin/features/${selectedFeature.id}` : '/admin/features';
      const method = selectedFeature ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(editedFeatureInfo)
      });

      if (response.ok) {
        alert(`기능이 성공적으로 ${selectedFeature ? '수정' : '생성'}되었습니다.`);
        setShowFeatureModal(false);
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`기능 ${selectedFeature ? '수정' : '생성'} 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error(`기능 ${selectedFeature ? '수정' : '생성'} 중 오류:`, error);
      alert(`기능 ${selectedFeature ? '수정' : '생성'} 중 오류가 발생했습니다.`);
    }
  };

  const deleteFeature = async (featureId: number) => {
    if (!confirm('정말로 이 기능을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/features/${featureId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('기능이 성공적으로 삭제되었습니다.');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`기능 삭제 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('기능 삭제 중 오류:', error);
      alert('기능 삭제 중 오류가 발생했습니다.');
    }
  };

  // ===========================================
  // CSV 내보내기 기능
  // ===========================================

  const exportUsersToCSV = () => {
    const headers = ['실명', '이메일', '전화번호', '부서', '직책', '상태', '관리자', '그룹', '가입일'];
    const csvData = [
      headers,
      ...filteredUsers.map(user => [
        user.real_name,
        user.email,
        user.phone_number || '',
        user.department || '',
        user.position || '',
        user.is_active ? '활성' : '비활성',
        user.is_admin ? '예' : '아니오',
        user.group?.name || '',
        formatDate(user.created_at)
      ])
    ];

    const csvContent = csvData.map(row => 
      row.map(field => `"${field}"`).join(',')
    ).join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `users_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // ===========================================
  // 비밀번호 재설정 기능
  // ===========================================

  const resetPassword = async () => {
    if (!passwordData.new_password) {
      alert('새 비밀번호를 입력해주세요.');
      return;
    }

    if (passwordData.new_password.length < 6) {
      alert('비밀번호는 최소 6자 이상이어야 합니다.');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/admin/users/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: passwordData.user_id,
          new_password: passwordData.new_password
        })
      });

      if (response.ok) {
        alert('비밀번호가 성공적으로 재설정되었습니다.');
        setShowPasswordModal(false);
        setPasswordData({user_id: '', new_password: ''});
      } else {
        const errorData = await response.json();
        alert(`비밀번호 재설정 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('비밀번호 재설정 중 오류:', error);
      alert('비밀번호 재설정 중 오류가 발생했습니다.');
    }
  };

  // ===========================================
  // 그룹 관리 기능
  // ===========================================

  const openGroupModal = async (group: Group | null = null) => {
    if (group) {
      setSelectedGroup(group);
      setEditedGroupInfo({
        name: group.name,
        description: group.description
      });
      // 그룹의 기존 기능들을 선택된 상태로 설정
      setSelectedGroupFeatures(group.features?.map(f => f.id) || []);
      setIsEditingGroup(true);
    } else {
      setSelectedGroup(null);
      setEditedGroupInfo({
        name: '',
        description: ''
      });
      setSelectedGroupFeatures([]);
      setIsEditingGroup(false);
    }
    setShowGroupModal(true);
  };

  const saveGroup = async () => {
    if (!editedGroupInfo.name) {
      alert('그룹명은 필수 입력 항목입니다.');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const url = selectedGroup ? `/admin/groups/${selectedGroup.id}` : '/admin/groups';
      const method = selectedGroup ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(editedGroupInfo)
      });

      if (response.ok) {
        const groupData = await response.json();
        const groupId = selectedGroup ? selectedGroup.id : groupData.id;
        
        // 기능 권한 업데이트 (별도 API 호출)
        const featuresResponse = await fetch('/admin/groups/features', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            group_id: groupId,
            feature_ids: selectedGroupFeatures
          })
        });

        if (featuresResponse.ok) {
          alert(`그룹이 성공적으로 ${selectedGroup ? '수정' : '생성'}되었습니다.`);
          setShowGroupModal(false);
          fetchData();
        } else {
          alert('그룹은 생성되었지만 기능 권한 설정에 실패했습니다.');
          setShowGroupModal(false);
          fetchData();
        }
      } else {
        const errorData = await response.json();
        alert(`그룹 ${selectedGroup ? '수정' : '생성'} 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error(`그룹 ${selectedGroup ? '수정' : '생성'} 중 오류:`, error);
      alert(`그룹 ${selectedGroup ? '수정' : '생성'} 중 오류가 발생했습니다.`);
    }
  };

  const deleteGroup = async (groupId: number) => {
    if (!confirm('정말로 이 그룹을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/admin/groups/${groupId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('그룹이 성공적으로 삭제되었습니다.');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`그룹 삭제 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('그룹 삭제 중 오류:', error);
      alert('그룹 삭제 중 오류가 발생했습니다.');
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.real_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.department?.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (!matchesSearch) return false;

    switch (filterStatus) {
      case 'active':
        return user.is_active && user.approval_status === 'approved';
      case 'inactive':
        return !user.is_active;
      case 'pending':
        return user.approval_status === 'pending';
      default:
        return true;
    }
  });

  const stats = {
    total: users.length,
    active: users.filter(u => u.is_active && u.approval_status === 'approved').length,
    pending: users.filter(u => u.approval_status === 'pending').length,
    inactive: users.filter(u => !u.is_active).length
  };



  const getStatusBadge = (user: User) => {
    if (user.approval_status === 'pending') {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 border border-yellow-200">대기중</span>;
    } else if (!user.is_active) {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800 border border-red-200">비활성</span>;
    } else {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 border border-green-200">활성</span>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-gray-200 border-t-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">관리자 페이지를 로딩하는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-gradient-to-br from-gray-50 to-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 font-display">
                시스템 관리
              </h1>
              <p className="text-gray-600 mt-1">
                사용자, 기능, 그룹을 관리하고 시스템을 모니터링합니다
              </p>
            </div>
            
            <button
              onClick={() => fetchData()}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors duration-200 shadow-sm hover:shadow-md"
            >
              <RefreshCw className="w-4 h-4" />
              <span>새로고침</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* 통계 카드 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center">
                  <div className="p-3 bg-blue-50 rounded-xl">
                    <Users className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">전체 사용자</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center">
                  <div className="p-3 bg-green-50 rounded-xl">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">활성 사용자</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.active}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center">
                  <div className="p-3 bg-yellow-50 rounded-xl">
                    <Clock className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">승인 대기</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center">
                  <div className="p-3 bg-red-50 rounded-xl">
                    <XCircle className="w-6 h-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">비활성</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.inactive}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 빠른 액션 */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">빠른 액션</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => setActiveTab('users')}
                  className="flex items-center p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <Users className="w-5 h-5 text-gray-600 mr-3" />
                  <span className="text-gray-900 font-medium">사용자 관리</span>
                  <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
                </button>

                <button
                  onClick={() => setActiveTab('features')}
                  className="flex items-center p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <Settings className="w-5 h-5 text-gray-600 mr-3" />
                  <span className="text-gray-900 font-medium">기능 관리</span>
                  <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
                </button>

                <button
                  onClick={() => setActiveTab('groups')}
                  className="flex items-center p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <Shield className="w-5 h-5 text-gray-600 mr-3" />
                  <span className="text-gray-900 font-medium">그룹 관리</span>
                  <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="bg-white rounded-2xl border border-gray-100 mb-6">
          <div className="flex space-x-1 p-2">
            {[
              { key: 'dashboard', label: '대시보드', icon: Database },
              { key: 'users', label: '사용자 관리', icon: Users },
              { key: 'features', label: '기능 관리', icon: Settings },
              { key: 'groups', label: '그룹 관리', icon: Shield }
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-200 ${
                  activeTab === key
                    ? 'bg-gray-900 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            {/* 검색 및 필터 */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
                <div className="flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="사용자 검색..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    />
                  </div>

                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value as any)}
                    className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-200"
                  >
                    <option value="all">전체 상태</option>
                    <option value="active">활성</option>
                    <option value="pending">승인 대기</option>
                    <option value="inactive">비활성</option>
                  </select>
                </div>

                <div className="flex space-x-2">
                  <button 
                    onClick={exportUsersToCSV}
                    className="flex items-center space-x-2 px-3 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>내보내기</span>
                  </button>
                  <button 
                    onClick={openAddUserModal}
                    className="flex items-center space-x-2 px-3 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    <span>사용자 추가</span>
                  </button>
                </div>
              </div>
            </div>

            {/* 사용자 목록 */}
            <div className="bg-white rounded-2xl border border-gray-100">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gray-50 border-b border-gray-100">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">사용자</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">연락처</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">부서/직책</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상태</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">가입일</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">액션</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-medium text-gray-600">
                                {user.real_name?.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="flex items-center space-x-2">
                                <div className="text-sm font-medium text-gray-900">{user.real_name}</div>
                                {user.is_admin && (
                                  <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">관리자</span>
                                )}
                              </div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {user.phone_number || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          <div>{user.department || '-'}</div>
                          <div className="text-gray-500">{user.position || '-'}</div>
                        </td>
                        <td className="px-6 py-4">
                          {getStatusBadge(user)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {formatDate(user.created_at)}
                        </td>
                        <td className="px-6 py-4 text-sm font-medium">
                          <div className="flex items-center space-x-1">
                            <button
                              onClick={() => openUserModal(user)}
                              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                              title="편집"
                            >
                              <Edit3 className="w-4 h-4 text-gray-500" />
                            </button>
                            
                            <button
                              onClick={() => {
                                setPasswordData({user_id: user.id, new_password: ''});
                                setShowPasswordModal(true);
                              }}
                              className="p-1.5 hover:bg-blue-100 rounded-lg transition-colors"
                              title="비밀번호 재설정"
                            >
                              <Key className="w-4 h-4 text-blue-600" />
                            </button>
                            
                            {user.approval_status === 'pending' && (
                              <>
                                <button
                                  onClick={() => updateUserStatus(user.id, 'approved', true)}
                                  className="p-1.5 hover:bg-green-100 rounded-lg transition-colors"
                                  title="승인"
                                >
                                  <UserCheck className="w-4 h-4 text-green-600" />
                                </button>
                                <button
                                  onClick={() => updateUserStatus(user.id, 'rejected', false)}
                                  className="p-1.5 hover:bg-red-100 rounded-lg transition-colors"
                                  title="거부"
                                >
                                  <UserX className="w-4 h-4 text-red-600" />
                                </button>
                              </>
                            )}
                            
                            {user.is_active ? (
                              <button
                                onClick={() => updateUserStatus(user.id, user.approval_status, false)}
                                className="p-1.5 hover:bg-yellow-100 rounded-lg transition-colors"
                                title="비활성화"
                              >
                                <EyeOff className="w-4 h-4 text-yellow-600" />
                              </button>
                            ) : (
                              <button
                                onClick={() => updateUserStatus(user.id, 'approved', true)}
                                className="p-1.5 hover:bg-green-100 rounded-lg transition-colors"
                                title="활성화"
                              >
                                <Eye className="w-4 h-4 text-green-600" />
                              </button>
                            )}
                            
                            <button
                              onClick={() => deleteUser(user.id)}
                              className="p-1.5 hover:bg-red-100 rounded-lg transition-colors"
                              title="삭제"
                            >
                              <Trash2 className="w-4 h-4 text-red-500" />
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

        {/* Features Tab */}
        {activeTab === 'features' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">기능 관리</h2>
              <button 
                onClick={() => openFeatureModal()}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>기능 추가</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature) => (
                <div key={feature.id} className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <span className="text-lg">{feature.icon}</span>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-gray-900">{feature.display_name}</h3>
                        <p className="text-xs text-gray-500">{feature.category}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        feature.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {feature.is_active ? '활성' : '비활성'}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{feature.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">{feature.url_path}</span>
                    <div className="flex space-x-1">
                      <button 
                        onClick={() => openFeatureModal(feature)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                        title="편집"
                      >
                        <Edit3 className="w-3.5 h-3.5 text-gray-500" />
                      </button>
                      <button 
                        onClick={() => deleteFeature(feature.id)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                        title="삭제"
                      >
                        <Trash2 className="w-3.5 h-3.5 text-red-500" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Groups Tab */}
        {activeTab === 'groups' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">그룹 관리</h2>
              <button 
                onClick={() => openGroupModal()}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>그룹 추가</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {groups.map((group) => (
                <div key={group.id} className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{group.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">{group.description}</p>
                    </div>
                    <div className="flex space-x-1">
                      <button 
                        onClick={() => openGroupModal(group)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                        title="편집"
                      >
                        <Edit3 className="w-4 h-4 text-gray-500" />
                      </button>
                      <button 
                        onClick={() => deleteGroup(group.id)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                        title="삭제"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">사용자 수</span>
                    <span className="font-medium text-gray-900">{group.users_count || 0}명</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm mt-2">
                    <span className="text-gray-600">기능 수</span>
                    <span className="font-medium text-gray-900">{group.features?.length || 0}개</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 기존 모달들은 유지 */}
      {/* User Modal */}
      {showUserModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 border border-gray-100">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">사용자 정보</h3>
            </div>
            <div className="p-6 space-y-4">
              {isEditingUserInfo ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">실명</label>
                    <input
                      type="text"
                      value={editedUserInfo.real_name}
                      onChange={(e) => setEditedUserInfo({...editedUserInfo, real_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">표시명</label>
                    <input
                      type="text"
                      value={editedUserInfo.display_name}
                      onChange={(e) => setEditedUserInfo({...editedUserInfo, display_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">전화번호</label>
                    <input
                      type="text"
                      value={editedUserInfo.phone_number}
                      onChange={(e) => setEditedUserInfo({...editedUserInfo, phone_number: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">부서</label>
                    <input
                      type="text"
                      value={editedUserInfo.department}
                      onChange={(e) => setEditedUserInfo({...editedUserInfo, department: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">직책</label>
                    <input
                      type="text"
                      value={editedUserInfo.position}
                      onChange={(e) => setEditedUserInfo({...editedUserInfo, position: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">그룹</label>
                    <select
                      value={selectedGroupId || ''}
                      onChange={(e) => setSelectedGroupId(e.target.value ? parseInt(e.target.value) : null)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    >
                      <option value="">그룹 선택</option>
                      {groups.map(group => (
                        <option key={group.id} value={group.id}>{group.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div><strong>실명:</strong> {selectedUser.real_name}</div>
                  <div><strong>이메일:</strong> {selectedUser.email}</div>
                  <div><strong>전화번호:</strong> {selectedUser.phone_number || '없음'}</div>
                  <div><strong>부서:</strong> {selectedUser.department || '없음'}</div>
                  <div><strong>직책:</strong> {selectedUser.position || '없음'}</div>
                  <div><strong>그룹:</strong> {selectedUser.group?.name || '없음'}</div>
                  <div><strong>관리자:</strong> {selectedUser.is_admin ? '예' : '아니오'}</div>
                  <div><strong>상태:</strong> {getStatusBadge(selectedUser)}</div>
                </div>
              )}
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              {isEditingUserInfo ? (
                <>
                  <button
                    onClick={() => setIsEditingUserInfo(false)}
                    className="px-4 py-2 text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    취소
                  </button>
                  <button
                    onClick={saveUserInfo}
                    className="px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
                  >
                    저장
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setShowUserModal(false)}
                    className="px-4 py-2 text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    닫기
                  </button>
                  <button
                    onClick={() => setIsEditingUserInfo(true)}
                    className="px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
                  >
                    편집
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 border border-gray-100">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">새 사용자 추가</h3>
            </div>
            <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">실명 *</label>
                  <input
                    type="text"
                    value={newUserInfo.real_name}
                    onChange={(e) => setNewUserInfo({...newUserInfo, real_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="실명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">표시명</label>
                  <input
                    type="text"
                    value={newUserInfo.display_name}
                    onChange={(e) => setNewUserInfo({...newUserInfo, display_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="표시명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">이메일 *</label>
                  <input
                    type="email"
                    value={newUserInfo.email}
                    onChange={(e) => setNewUserInfo({...newUserInfo, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="이메일을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">비밀번호 *</label>
                  <input
                    type="password"
                    value={newUserInfo.password}
                    onChange={(e) => setNewUserInfo({...newUserInfo, password: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="비밀번호를 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">전화번호</label>
                  <input
                    type="text"
                    value={newUserInfo.phone_number}
                    onChange={(e) => setNewUserInfo({...newUserInfo, phone_number: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="전화번호를 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">부서</label>
                  <input
                    type="text"
                    value={newUserInfo.department}
                    onChange={(e) => setNewUserInfo({...newUserInfo, department: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="부서를 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">직책</label>
                  <input
                    type="text"
                    value={newUserInfo.position}
                    onChange={(e) => setNewUserInfo({...newUserInfo, position: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="직책을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">그룹</label>
                  <select
                    value={newUserInfo.group_id || ''}
                    onChange={(e) => setNewUserInfo({...newUserInfo, group_id: e.target.value ? parseInt(e.target.value) : null})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                  >
                    <option value="">그룹 선택</option>
                    {groups.map(group => (
                      <option key={group.id} value={group.id}>{group.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">소개</label>
                <textarea
                  value={newUserInfo.bio}
                  onChange={(e) => setNewUserInfo({...newUserInfo, bio: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                  placeholder="사용자 소개를 입력하세요"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_admin"
                  checked={newUserInfo.is_admin}
                  onChange={(e) => setNewUserInfo({...newUserInfo, is_admin: e.target.checked})}
                  className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
                />
                <label htmlFor="is_admin" className="ml-2 block text-sm text-gray-900">
                  관리자 권한 부여
                </label>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowAddUserModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                취소
              </button>
              <button
                onClick={createUser}
                className="px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
              >
                사용자 생성
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Password Reset Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 border border-gray-100">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">비밀번호 재설정</h3>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">새 비밀번호</label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                  placeholder="새 비밀번호를 입력하세요"
                  autoFocus
                />
                <p className="text-xs text-gray-500 mt-1">최소 6자 이상 입력해주세요.</p>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowPasswordModal(false);
                  setPasswordData({user_id: '', new_password: ''});
                }}
                className="px-4 py-2 text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                취소
              </button>
              <button
                onClick={resetPassword}
                className="px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
              >
                비밀번호 재설정
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Feature Modal */}
      {showFeatureModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 border border-gray-100">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedFeature ? '기능 편집' : '새 기능 추가'}
              </h3>
            </div>
            <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">기능명 *</label>
                  <input
                    type="text"
                    value={editedFeatureInfo.name}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="기능명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">표시명 *</label>
                  <input
                    type="text"
                    value={editedFeatureInfo.display_name}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, display_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="표시명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
                  <input
                    type="text"
                    value={editedFeatureInfo.category}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="카테고리를 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">아이콘</label>
                  <input
                    type="text"
                    value={editedFeatureInfo.icon}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, icon: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="아이콘 (예: 🚀)"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">URL 경로</label>
                  <input
                    type="text"
                    value={editedFeatureInfo.url_path}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, url_path: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="URL 경로를 입력하세요 (예: /dashboard)"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">설명</label>
                <textarea
                  value={editedFeatureInfo.description}
                  onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                  placeholder="기능 설명을 입력하세요"
                />
              </div>
              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={editedFeatureInfo.is_active}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, is_active: e.target.checked})}
                    className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                    활성화
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="requires_approval"
                    checked={editedFeatureInfo.requires_approval}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, requires_approval: e.target.checked})}
                    className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
                  />
                  <label htmlFor="requires_approval" className="ml-2 block text-sm text-gray-900">
                    승인 필요
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_external"
                    checked={editedFeatureInfo.is_external}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, is_external: e.target.checked})}
                    className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_external" className="ml-2 block text-sm text-gray-900">
                    외부 링크
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="open_in_new_tab"
                    checked={editedFeatureInfo.open_in_new_tab}
                    onChange={(e) => setEditedFeatureInfo({...editedFeatureInfo, open_in_new_tab: e.target.checked})}
                    className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
                  />
                  <label htmlFor="open_in_new_tab" className="ml-2 block text-sm text-gray-900">
                    새 탭에서 열기
                  </label>
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowFeatureModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                취소
              </button>
              <button
                onClick={saveFeature}
                className="px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
              >
                {selectedFeature ? '수정' : '생성'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Group Modal */}
      {showGroupModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl mx-4 border border-gray-100">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedGroup ? '그룹 편집' : '새 그룹 추가'}
              </h3>
            </div>
            <div className="p-6 space-y-6 max-h-96 overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">그룹명 *</label>
                  <input
                    type="text"
                    value={editedGroupInfo.name}
                    onChange={(e) => setEditedGroupInfo({...editedGroupInfo, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="그룹명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">설명</label>
                  <input
                    type="text"
                    value={editedGroupInfo.description}
                    onChange={(e) => setEditedGroupInfo({...editedGroupInfo, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-gray-300"
                    placeholder="그룹 설명을 입력하세요"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">그룹 기능 선택</label>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-y-auto p-3 border border-gray-200 rounded-lg">
                  {availableFeatures.map((feature) => (
                    <div key={feature.id} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`feature-${feature.id}`}
                        checked={selectedGroupFeatures.includes(feature.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedGroupFeatures([...selectedGroupFeatures, feature.id]);
                          } else {
                            setSelectedGroupFeatures(selectedGroupFeatures.filter(id => id !== feature.id));
                          }
                        }}
                        className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
                      />
                      <label htmlFor={`feature-${feature.id}`} className="ml-2 text-sm text-gray-900 flex items-center">
                        <span className="mr-1">{feature.icon}</span>
                        {feature.display_name}
                      </label>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  선택된 기능: {selectedGroupFeatures.length}개
                </p>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowGroupModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                취소
              </button>
              <button
                onClick={saveGroup}
                className="px-4 py-2 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
              >
                {selectedGroup ? '수정' : '생성'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage; 