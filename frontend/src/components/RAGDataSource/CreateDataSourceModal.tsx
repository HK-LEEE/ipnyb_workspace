/**
 * RAG 데이터소스 생성 모달 컴포넌트
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { X, User, Users } from 'lucide-react';
import axios from 'axios';
import { CreateDataSourceData } from '../../types/ragDataSource';

// 그룹 타입 정의
interface Group {
  id: number;
  name: string;
  description?: string;
}

interface CreateDataSourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateDataSourceData) => void;
  isLoading: boolean;
}

const CreateDataSourceModal: React.FC<CreateDataSourceModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isLoading
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [ownerType, setOwnerType] = useState<'USER' | 'GROUP'>('USER');
  const [selectedGroupId, setSelectedGroupId] = useState<number | undefined>();

  // 그룹 목록 조회
  const { data: groups } = useQuery<Group[]>(
    'groups',
    async () => {
      try {
        const response = await axios.get('/admin/groups');
        return response.data;
      } catch (error) {
        console.error('Failed to fetch groups:', error);
        return [];
      }
    },
    {
      enabled: isOpen && ownerType === 'GROUP'
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      name,
      description: description || undefined,
      owner_type: ownerType,
      group_id: ownerType === 'GROUP' ? selectedGroupId : undefined
    });
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setOwnerType('USER');
    setSelectedGroupId(undefined);
    onClose();
  };

  useEffect(() => {
    if (groups && groups.length > 0 && !selectedGroupId) {
      setSelectedGroupId(groups[0].id);
    }
  }, [groups, selectedGroupId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">새 RAG 데이터소스 생성</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isLoading}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              데이터소스 이름 *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="예: 고객 지원 문서"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              설명 (선택사항)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="데이터소스에 대한 간단한 설명을 입력하세요"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              소유자 타입 *
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="USER"
                  checked={ownerType === 'USER'}
                  onChange={(e) => setOwnerType(e.target.value as 'USER')}
                  className="mr-2"
                  disabled={isLoading}
                />
                <User className="h-4 w-4 mr-1" />
                개인 전용 (나만 사용)
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="GROUP"
                  checked={ownerType === 'GROUP'}
                  onChange={(e) => setOwnerType(e.target.value as 'GROUP')}
                  className="mr-2"
                  disabled={isLoading}
                />
                <Users className="h-4 w-4 mr-1" />
                그룹 공유 (팀원과 공유)
              </label>
            </div>
          </div>

          {ownerType === 'GROUP' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                그룹 선택 *
              </label>
              <select
                value={selectedGroupId || ''}
                onChange={(e) => setSelectedGroupId(Number(e.target.value))}
                required
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              >
                <option value="">그룹을 선택하세요</option>
                {groups?.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                    {group.description && ` - ${group.description}`}
                  </option>
                ))}
              </select>
              {groups && groups.length === 0 && (
                <p className="text-sm text-gray-500 mt-1">
                  사용 가능한 그룹이 없습니다. 관리자에게 문의하세요.
                </p>
              )}
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              disabled={isLoading}
            >
              취소
            </button>
            <button
              type="submit"
              disabled={isLoading || !name.trim() || (ownerType === 'GROUP' && !selectedGroupId)}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? '생성 중...' : '생성'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateDataSourceModal; 