/**
 * 문서 목록 및 관리 모달 컴포넌트
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  X, 
  FileText, 
  Trash2, 
  Search, 
  ChevronLeft, 
  ChevronRight,
  AlertTriangle,
  Clock,
  User,
  HardDrive,
  Download,
  File,
  Folder
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import ragDataSourceService from '../../services/ragDataSourceService';

interface Document {
  id: string;
  filename: string;
  chunk_index: number;
  total_chunks: number;
  file_size: number;
  upload_time: string;
  uploaded_by: string;
  preview: string;
  content_length: number;
}

interface DocumentListResponse {
  documents: Document[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface StoredFile {
  filename: string;
  file_path: string;
  file_size: number;
  created_time: string;
  modified_time: string;
  relative_path: string;
}

interface StorageStats {
  owner_type: string;
  owner_id: string;
  total_size_bytes: number;
  total_size_mb: number;
  file_count: number;
  storage_path: string;
}

interface DocumentListModalProps {
  isOpen: boolean;
  onClose: () => void;
  dataSourceId: number;
  dataSourceName: string;
}

const DocumentListModal: React.FC<DocumentListModalProps> = ({
  isOpen,
  onClose,
  dataSourceId,
  dataSourceName
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set());
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentsData, setDocumentsData] = useState<DocumentListResponse | null>(null);
  const [totalPages, setTotalPages] = useState(1);
  const [storedFiles, setStoredFiles] = useState<StoredFile[]>([]);
  const [storageStats, setStorageStats] = useState<StorageStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'documents' | 'files'>('documents');
  const pageSize = 20;
  const queryClient = useQueryClient();

  const token = localStorage.getItem('token');

  // 문서 목록 조회 쿼리
  const { data: documentsQueryData, isLoading, error: queryError } = useQuery(
    ['documents', dataSourceId, currentPage],
    () => ragDataSourceService.getDocuments(dataSourceId, currentPage, pageSize),
    {
      enabled: isOpen && activeTab === 'documents',
      onSuccess: (data) => {
        setDocumentsData(data);
        setDocuments(data.documents || []);
        setTotalPages(data.total_pages || 1);
      },
      onError: (err) => {
        console.error('Error fetching documents:', err);
        setError('문서 목록을 불러오는데 실패했습니다.');
      }
    }
  );

  // 문서 삭제 뮤테이션
  const deleteDocumentMutation = useMutation(
    (documentId: string) => ragDataSourceService.deleteDocument(dataSourceId, documentId),
    {
      onSuccess: () => {
        toast.success('문서가 삭제되었습니다.');
        queryClient.invalidateQueries(['documents', dataSourceId]);
        if (activeTab === 'documents') {
          fetchDocuments();
        }
      },
      onError: () => {
        toast.error('문서 삭제에 실패했습니다.');
      }
    }
  );

  useEffect(() => {
    if (isOpen) {
      if (activeTab === 'documents') {
        // React Query가 자동으로 처리
      } else {
        fetchStoredFiles();
      }
    }
  }, [isOpen, activeTab]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/llmops/rag-datasources/${dataSourceId}/documents?page=${currentPage}&page_size=${pageSize}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDocumentsData(data);
        setDocuments(data.documents || []);
        setTotalPages(Math.ceil((data.total_documents || 0) / pageSize));
      } else {
        console.error('Failed to fetch documents');
        setError('문서 목록을 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('문서 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStoredFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/llmops/rag-datasources/${dataSourceId}/stored-files`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setStoredFiles(data.stored_files || []);
        setStorageStats(data.storage_stats || null);
      } else {
        console.error('Failed to fetch stored files');
        setError('저장된 파일 목록을 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Error fetching stored files:', error);
      setError('저장된 파일 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (documentId: string) => {
    if (!confirm('이 문서를 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/llmops/rag-datasources/${dataSourceId}/documents/${documentId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        fetchDocuments();
        toast.success('문서가 삭제되었습니다.');
      } else {
        toast.error('문서 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('문서 삭제 중 오류가 발생했습니다.');
    }
  };

  const deleteStoredFile = async (filePath: string) => {
    if (!confirm('이 파일을 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/llmops/rag-datasources/${dataSourceId}/stored-files?file_path=${encodeURIComponent(filePath)}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        fetchStoredFiles();
        toast.success('파일이 삭제되었습니다.');
      } else {
        toast.error('파일 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error deleting stored file:', error);
      toast.error('파일 삭제 중 오류가 발생했습니다.');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedDocuments.size === 0) return;
    if (!confirm(`선택된 ${selectedDocuments.size}개 항목을 삭제하시겠습니까?`)) return;

    const deletePromises = Array.from(selectedDocuments).map(id => {
      if (activeTab === 'documents') {
        return deleteDocument(id);
      } else {
        const file = storedFiles.find(f => f.file_path === id);
        return file ? deleteStoredFile(file.file_path) : Promise.resolve();
      }
    });

    try {
      await Promise.all(deletePromises);
      setSelectedDocuments(new Set());
      if (activeTab === 'documents') {
        fetchDocuments();
      } else {
        fetchStoredFiles();
      }
    } catch (error) {
      console.error('Error in bulk delete:', error);
    }
  };

  // 파일 크기 포맷팅
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string) => {
    if (!dateString) return '알 수 없음';
    return new Date(dateString).toLocaleString('ko-KR');
  };

  // 필터링된 문서 목록
  const filteredDocuments = documents?.filter(doc =>
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.preview.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const filteredFiles = storedFiles.filter(file =>
    file.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-5/6 flex flex-col">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {dataSourceName} - 콘텐츠 관리
            </h2>
            {storageStats && (
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <HardDrive className="w-4 h-4" />
                  <span>저장소 사용량: {formatFileSize(storageStats.total_size_bytes)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Folder className="w-4 h-4" />
                  <span>파일 수: {storageStats.file_count}개</span>
                </div>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('documents')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'documents'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              문서 청크
            </div>
          </button>
          <button
            onClick={() => setActiveTab('files')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'files'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <File className="w-4 h-4" />
              원본 파일
            </div>
          </button>
        </div>

        {/* 검색 및 액션 바 */}
        <div className="p-4 border-b bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder={activeTab === 'documents' ? "문서 검색..." : "파일 검색..."}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {selectedDocuments.size > 0 && (
              <button
                onClick={handleBulkDelete}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                선택 삭제 ({selectedDocuments.size})
              </button>
            )}
          </div>
        </div>

        {/* 문서 목록 */}
        <div className="flex-1 overflow-auto">
          {(loading || isLoading) ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">
                  {activeTab === 'documents' ? '문서 목록을 불러오는 중...' : '파일 목록을 불러오는 중...'}
                </p>
              </div>
            </div>
          ) : (error || queryError) ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-red-600">
                <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                <p>{error || '데이터를 불러오는데 실패했습니다.'}</p>
              </div>
            </div>
          ) : activeTab === 'documents' ? (
            filteredDocuments.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-500">
                  <FileText className="w-8 h-8 mx-auto mb-2" />
                  <p>문서가 없습니다.</p>
                </div>
              </div>
            ) : (
              <div className="p-4">
                <div className="grid gap-4">
                  {filteredDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
                        selectedDocuments.has(doc.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          <input
                            type="checkbox"
                            checked={selectedDocuments.has(doc.id)}
                            onChange={(e) => {
                              const newSelected = new Set(selectedDocuments);
                              if (e.target.checked) {
                                newSelected.add(doc.id);
                              } else {
                                newSelected.delete(doc.id);
                              }
                              setSelectedDocuments(newSelected);
                            }}
                            className="mt-1"
                          />
                          
                          <FileText className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                          
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium text-gray-900 truncate">
                              {doc.filename}
                            </h3>
                            
                            <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                              <span className="flex items-center gap-1">
                                <HardDrive className="w-3 h-3" />
                                {formatFileSize(doc.file_size)}
                              </span>
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatDate(doc.upload_time)}
                              </span>
                              {doc.uploaded_by && (
                                <span className="flex items-center gap-1">
                                  <User className="w-3 h-3" />
                                  {doc.uploaded_by}
                                </span>
                              )}
                            </div>
                            
                            <div className="mt-2 text-sm text-gray-600">
                              <p className="line-clamp-2">{doc.preview}</p>
                            </div>
                            
                            <div className="mt-2 text-xs text-gray-400">
                              청크 {doc.chunk_index + 1}/{doc.total_chunks} • 
                              내용 길이: {doc.content_length.toLocaleString()}자
                            </div>
                          </div>
                        </div>
                        
                        <button
                          onClick={() => deleteDocument(doc.id)}
                          disabled={deleteDocumentMutation.isLoading}
                          className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                          title="문서 삭제"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          ) : (
            filteredFiles.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-500">
                  <File className="w-8 h-8 mx-auto mb-2" />
                  <p>저장된 파일이 없습니다.</p>
                </div>
              </div>
            ) : (
              <div className="p-4">
                <div className="grid gap-4">
                  {filteredFiles.map((file) => (
                    <div
                      key={file.file_path}
                      className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
                        selectedDocuments.has(file.file_path) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          <input
                            type="checkbox"
                            checked={selectedDocuments.has(file.file_path)}
                            onChange={(e) => {
                              const newSelected = new Set(selectedDocuments);
                              if (e.target.checked) {
                                newSelected.add(file.file_path);
                              } else {
                                newSelected.delete(file.file_path);
                              }
                              setSelectedDocuments(newSelected);
                            }}
                            className="mt-1"
                          />
                          
                          <File className="w-5 h-5 text-gray-400 flex-shrink-0" />
                          
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium text-gray-900 truncate">
                              {file.filename}
                            </h3>
                            
                            <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                              <span className="flex items-center gap-1">
                                <HardDrive className="w-3 h-3" />
                                {formatFileSize(file.file_size)}
                              </span>
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatDate(file.created_time)}
                              </span>
                            </div>
                            
                            <div className="mt-2 text-xs text-gray-400">
                              경로: {file.relative_path}
                            </div>
                          </div>
                        </div>
                        
                        <button
                          onClick={() => deleteStoredFile(file.file_path)}
                          className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="파일 삭제"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          )}
        </div>

        {/* 페이지네이션 */}
        {activeTab === 'documents' && documentsData && documentsData.total_pages > 1 && (
          <div className="p-4 border-t bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                총 {documentsData.total_count}개 문서 중 {((currentPage - 1) * pageSize) + 1}-
                {Math.min(currentPage * pageSize, documentsData.total_count)}개 표시
              </div>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="p-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                
                <span className="px-3 py-1 text-sm">
                  {currentPage} / {documentsData.total_pages}
                </span>
                
                <button
                  onClick={() => setCurrentPage(prev => Math.min(documentsData.total_pages, prev + 1))}
                  disabled={currentPage === documentsData.total_pages}
                  className="p-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentListModal; 