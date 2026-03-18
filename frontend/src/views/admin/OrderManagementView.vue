<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Search, 
  Loader2, 
  ChevronRight, 
  Clock, 
  CheckCircle2, 
  Truck, 
  XCircle, 
  AlertCircle,
  FileText,
  User,
  CreditCard,
  MessageSquare
} from 'lucide-vue-next'
import { adminOrderService } from '@/services/adminOrderService'
import type { Order, OrderDetail } from '@/types/order'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import Pagination from '@/components/ui/Pagination.vue'
import { useToast } from '@/composables/useToast'
import { format } from 'date-fns'

const LIMIT = 10
const orders = ref<Order[]>([])
const total = ref(0)
const currentPage = ref(1)
const isLoading = ref(true)
const { showSuccess, showError } = useToast()

// Filters
const statusFilter = ref<string>('ALL')
const searchId = ref('')

// Order Detail
const selectedOrderId = ref<string | null>(null)
const orderDetail = ref<OrderDetail | null>(null)
const isDetailLoading = ref(false)
const isSheetOpen = ref(false)

const updatingStatus = ref<string>('')
const adminNote = ref('')
const isUpdating = ref(false)

const loadOrders = async () => {
  try {
    isLoading.value = true
    const response = await adminOrderService.getOrders({
      page: currentPage.value,
      limit: LIMIT,
      status: statusFilter.value === 'ALL' ? undefined : statusFilter.value
    })
    orders.value = response.orders
    total.value = response.total
  } catch (error) {
    showError('無法載入訂單列表')
  } finally {
    isLoading.value = false
  }
}

const onFilterChange = () => {
  currentPage.value = 1
  loadOrders()
}

const viewDetail = async (orderId: string) => {
  selectedOrderId.value = orderId
  isSheetOpen.value = true
  isDetailLoading.value = true
  try {
    orderDetail.value = await adminOrderService.getOrderDetail(orderId)
    adminNote.value = orderDetail.value.admin_note || ''
  } catch (error) {
    showError('無法獲取訂單詳情')
    isSheetOpen.value = false
  } finally {
    isDetailLoading.value = false
  }
}

const openUpdateDialog = (status: string) => {
  const statusLabel = getStatusBadge(status).label
  const warningText = status === 'CANCELLED' ? '\n\n此操作將會回補商品庫存。' : ''
  const confirmed = window.confirm(`確定要將訂單狀態更新為「${statusLabel}」嗎？${warningText}`)
  if (!confirmed) return

  updatingStatus.value = status
  handleUpdateOrder()
}

const handleUpdateOrder = async () => {
  if (!selectedOrderId.value) return
  
  try {
    isUpdating.value = true
    await adminOrderService.updateOrder(selectedOrderId.value, {
      status: updatingStatus.value || undefined,
      admin_note: adminNote.value
    })
    showSuccess('訂單已更新')
    // 重新加載詳情與列表
    orderDetail.value = await adminOrderService.getOrderDetail(selectedOrderId.value)
    loadOrders()
  } catch (error: any) {
    showError(error.response?.data?.detail || '更新失敗')
  } finally {
    isUpdating.value = false
  }
}

const saveNoteOnly = async () => {
  if (!selectedOrderId.value) return
  try {
    isUpdating.value = true
    await adminOrderService.updateOrder(selectedOrderId.value, {
      admin_note: adminNote.value
    })
    showSuccess('備註已儲存')
  } catch (error) {
    showError('儲存備註失敗')
  } finally {
    isUpdating.value = false
  }
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'PENDING': return { variant: 'outline', label: '待付款', icon: Clock }
    case 'PAID': return { variant: 'secondary', label: '已付款', icon: CheckCircle2 }
    case 'SHIPPED': return { variant: 'default', label: '已出貨', icon: Truck }
    case 'DELIVERED': return { variant: 'default', label: '已送達', icon: CheckCircle2 }
    case 'COMPLETED': return { variant: 'success', label: '已完成', icon: CheckCircle2 }
    case 'CANCELLED': return { variant: 'destructive', label: '已取消', icon: XCircle }
    case 'REFUNDING': return { variant: 'warning', label: '退款中', icon: AlertCircle }
    case 'REFUNDED': return { variant: 'outline', label: '已退款', icon: XCircle }
    default: return { variant: 'outline', label: status, icon: Clock }
  }
}

onMounted(() => {
  loadOrders()
})

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    return format(new Date(dateStr), 'yyyy-MM-dd HH:mm')
  } catch (e) {
    return dateStr
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h2 class="text-3xl font-bold tracking-tight">訂單管理</h2>
        <p class="text-muted-foreground">檢視與管理系統中的所有訂單</p>
      </div>
    </div>

    <!-- 篩選器 -->
    <Card>
      <CardContent class="pt-6">
        <div class="flex flex-col gap-4 md:flex-row">
          <div class="flex-1">
            <div class="relative">
              <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                v-model="searchId"
                placeholder="搜尋訂單編號..."
                class="pl-8"
                @keyup.enter="onFilterChange"
              />
            </div>
          </div>
          <div class="w-full md:w-[200px]">
            <select
              v-model="statusFilter"
              @change="onFilterChange"
              class="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="ALL">全部狀態</option>
              <option value="PENDING">待付款</option>
              <option value="PAID">已付款</option>
              <option value="SHIPPED">已出貨</option>
              <option value="DELIVERED">已送達</option>
              <option value="COMPLETED">已完成</option>
              <option value="CANCELLED">已取消</option>
              <option value="REFUNDING">退款中</option>
              <option value="REFUNDED">已退款</option>
            </select>
          </div>
          <Button variant="outline" @click="loadOrders">
            重新整理
          </Button>
        </div>
      </CardContent>
    </Card>

    <!-- 訂單列表 -->
    <Card>
      <CardContent class="p-0">
        <div v-if="isLoading" class="flex h-64 items-center justify-center">
          <Loader2 class="h-8 w-8 animate-spin text-primary" />
        </div>
        
        <div v-else-if="orders.length === 0" class="flex h-64 flex-col items-center justify-center text-muted-foreground">
          <FileText class="mb-2 h-12 w-12 opacity-20" />
          <p>找不到任何訂單</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-800 dark:text-gray-400">
              <tr>
                <th class="px-4 py-3">訂單編號</th>
                <th class="px-4 py-3">日期</th>
                <th class="px-4 py-3">金額</th>
                <th class="px-4 py-3">狀態</th>
                <th class="px-4 py-3 text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id" class="border-b dark:border-gray-700 hover:bg-gray-50/50">
                <td class="px-4 py-4 font-medium">{{ order.order_number }}</td>
                <td class="px-4 py-4">{{ formatDate(order.created_at) }}</td>
                <td class="px-4 py-4">${{ order.total_amount.toLocaleString() }}</td>
                <td class="px-4 py-4">
                <Badge :variant="getStatusBadge(order.status).variant as any" class="gap-1">
                  <component :is="getStatusBadge(order.status).icon" class="h-3 w-3" />
                  {{ getStatusBadge(order.status).label }}
                </Badge>
                </td>
                <td class="px-4 py-4 text-right">
                <Button variant="ghost" size="sm" @click="viewDetail(order.id)">
                  檢視
                  <ChevronRight class="ml-1 h-4 w-4" />
                </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>

    <!-- 分頁 -->
    <div v-if="total > LIMIT" class="flex justify-center">
      <Pagination
        :page="currentPage"
        :limit="LIMIT"
        :total="total"
        @update:page="(p) => { currentPage = p; loadOrders() }"
      />
    </div>

    <!-- 訂單詳情 Sheet -->
    <Sheet v-model:open="isSheetOpen">
      <SheetContent class="w-full sm:max-w-[600px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>訂單詳情</SheetTitle>
          <SheetDescription v-if="orderDetail">
            訂單編號: {{ orderDetail.order_number }}
          </SheetDescription>
        </SheetHeader>

        <div v-if="isDetailLoading" class="flex h-64 items-center justify-center">
          <Loader2 class="h-8 w-8 animate-spin text-primary" />
        </div>

        <div v-else-if="orderDetail" class="mt-6 space-y-8 pb-10">
          <!-- 狀態與時間 -->
          <div class="flex items-center justify-between">
            <Badge :variant="getStatusBadge(orderDetail.status).variant as any" class="text-base px-3 py-1 gap-1.5">
              <component :is="getStatusBadge(orderDetail.status).icon" class="h-4 w-4" />
              {{ getStatusBadge(orderDetail.status).label }}
            </Badge>
            <div class="text-sm text-muted-foreground text-right">
              <div>下單時間: {{ formatDate(orderDetail.created_at) }}</div>
              <div v-if="orderDetail.status_updated_at">
                最後更新: {{ formatDate(orderDetail.status_updated_at) }}
              </div>
            </div>
          </div>

          <!-- 操作按鈕 -->
          <div class="flex flex-wrap gap-2">
            <Button v-if="orderDetail.status === 'PENDING'" size="sm" @click="openUpdateDialog('PAID')">
              標記為已付款
            </Button>
            <Button v-if="orderDetail.status === 'PAID'" size="sm" @click="openUpdateDialog('SHIPPED')">
              標記為已出貨
            </Button>
            <Button v-if="['SHIPPED', 'DELIVERED'].includes(orderDetail.status)" size="sm" @click="openUpdateDialog('COMPLETED')">
              標記為已完成
            </Button>
            <Button 
              v-if="['PENDING', 'PAID'].includes(orderDetail.status)" 
              variant="destructive" 
              size="sm" 
              @click="openUpdateDialog('CANCELLED')"
            >
              取消訂單
            </Button>
            <Button 
              v-if="orderDetail.status === 'SHIPPED'" 
              variant="outline" 
              size="sm" 
              @click="openUpdateDialog('DELIVERED')"
            >
              更新為已送達
            </Button>
          </div>

          <!-- 客戶與配送資訊 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-3">
              <h4 class="font-semibold flex items-center gap-2">
                <User class="h-4 w-4" /> 收件資訊
              </h4>
              <div class="text-sm space-y-1">
                <p><span class="text-muted-foreground">姓名：</span>{{ orderDetail.recipient_name }}</p>
                <p><span class="text-muted-foreground">電話：</span>{{ orderDetail.recipient_phone }}</p>
                <p class="flex items-start gap-1">
                  <span class="text-muted-foreground shrink-0">地址：</span>
                  <span>{{ orderDetail.shipping_address }}</span>
                </p>
              </div>
            </div>
            <div class="space-y-3">
              <h4 class="font-semibold flex items-center gap-2">
                <CreditCard class="h-4 w-4" /> 付款資訊
              </h4>
              <div class="text-sm space-y-1">
                <p><span class="text-muted-foreground">方式：</span>{{ orderDetail.payment_method }}</p>
                <p><span class="text-muted-foreground">運費：</span>${{ orderDetail.shipping_fee?.toLocaleString() || 0 }}</p>
                <p class="text-lg font-bold"><span class="text-muted-foreground text-sm font-normal">總額：</span>${{ orderDetail.total_amount.toLocaleString() }}</p>
              </div>
            </div>
          </div>

          <!-- 訂單項目 -->
          <div class="space-y-3">
            <h4 class="font-semibold">商品項目</h4>
            <div class="border rounded-md divide-y">
              <div v-for="item in orderDetail.items" :key="item.id" class="p-3 flex justify-between items-center text-sm">
                <div>
                  <p class="font-medium">{{ item.product_name }}</p>
                  <p class="text-muted-foreground">${{ item.unit_price.toLocaleString() }} x {{ item.quantity }}</p>
                </div>
                <div class="font-semibold">${{ item.subtotal.toLocaleString() }}</div>
              </div>
            </div>
          </div>

          <!-- 管理員備註 -->
          <div class="space-y-3 pt-4 border-t">
            <h4 class="font-semibold flex items-center gap-2">
              <MessageSquare class="h-4 w-4" /> 管理員內部備註
            </h4>
            <textarea
              v-model="adminNote" 
              placeholder="僅限管理員可見的內部備註..." 
              rows="4"
              class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            ></textarea>
            <Button variant="outline" size="sm" :disabled="isUpdating" @click="saveNoteOnly">
              儲存備註
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  </div>
</template>
