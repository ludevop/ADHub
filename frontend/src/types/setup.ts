// Setup wizard types

export enum DNSBackendType {
  SAMBA_INTERNAL = 'SAMBA_INTERNAL',
  BIND9_DLZ = 'BIND9_DLZ',
  NONE = 'NONE'
}

export enum DomainFunctionLevel {
  LEVEL_2000 = '2000',
  LEVEL_2003 = '2003',
  LEVEL_2008 = '2008',
  LEVEL_2008_R2 = '2008_R2'
}

export interface DomainConfig {
  realm: string
  domain: string
  domain_name: string
  admin_password: string
  dns_backend: DNSBackendType
  dns_forwarder: string
  server_role: string
  host_ip?: string
  function_level: DomainFunctionLevel
}

export interface PrerequisiteCheck {
  check_name: string
  status: 'passed' | 'failed' | 'warning'
  message: string
  details?: string
}

export interface PrerequisitesResponse {
  all_passed: boolean
  checks: PrerequisiteCheck[]
}

export enum ProvisionStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface ProvisionResponse {
  status: ProvisionStatus
  message: string
  task_id?: string
  output?: string
  error?: string
}

export interface VerificationTest {
  test_name: string
  category: 'dns' | 'kerberos' | 'ldap' | 'services' | 'auth' | 'prerequisites'
  status: 'passed' | 'failed' | 'skipped' | 'running'
  message: string
  details?: string
  duration_ms?: number
}

export interface VerificationResponse {
  overall_status: 'passed' | 'failed' | 'partial'
  total_tests: number
  passed: number
  failed: number
  skipped: number
  tests: VerificationTest[]
  summary: string
}

export interface SetupStatusResponse {
  is_provisioned: boolean
  domain_info?: Record<string, string>
  last_provision_date?: string
}

export enum SetupStep {
  WELCOME = 0,
  PREREQUISITES = 1,
  DOMAIN_CONFIG = 2,
  DNS_CONFIG = 3,
  REVIEW = 4,
  PROVISION = 5,
  VERIFICATION = 6,
  COMPLETE = 7
}
