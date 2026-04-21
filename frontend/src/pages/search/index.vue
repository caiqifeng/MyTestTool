<template>
  <view class="page-container">
    <view class="search-page">
      <!-- 搜索头部 -->
      <view class="search-header">
        <view class="search-input-container">
          <view class="search-icon">🔍</view>
          <input
            class="search-input"
            v-model="searchKeyword"
            type="text"
            placeholder="搜索面包、糕点..."
            confirm-type="search"
            @confirm="handleSearch"
            @input="handleInput"
          />
          <view v-if="searchKeyword" class="clear-icon" @click="clearKeyword">
            ×
          </view>
        </view>
        <view class="cancel-btn" @click="handleCancel">
          <text class="cancel-text">取消</text>
        </view>
      </view>

      <!-- 热门搜索 -->
      <view v-if="!searchKeyword && searchHistory.length === 0" class="hot-search-section">
        <view class="section-title">热门搜索</view>
        <view class="hot-search-tags">
          <view
            v-for="tag in hotSearchTags"
            :key="tag"
            class="search-tag"
            @click="handleTagClick(tag)"
          >
            <text class="tag-text">{{ tag }}</text>
          </view>
        </view>
      </view>

      <!-- 搜索历史 -->
      <view v-if="!searchKeyword && searchHistory.length > 0" class="history-section">
        <view class="section-header">
          <text class="section-title">搜索历史</text>
          <text class="clear-history" @click="clearHistory">清空</text>
        </view>
        <view class="history-list">
          <view
            v-for="item in searchHistory"
            :key="item"
            class="history-item"
            @click="handleHistoryClick(item)"
          >
            <view class="history-icon">🕒</view>
            <text class="history-text">{{ item }}</text>
            <view class="delete-icon" @click.stop="deleteHistoryItem(item)">×</view>
          </view>
        </view>
      </view>

      <!-- 搜索结果建议 -->
      <view v-if="searchKeyword && searchSuggestions.length > 0" class="suggestions-section">
        <view class="section-title">搜索结果</view>
        <view class="suggestions-list">
          <view
            v-for="suggestion in searchSuggestions"
            :key="suggestion"
            class="suggestion-item"
            @click="handleSuggestionClick(suggestion)"
          >
            <view class="suggestion-icon">🔍</view>
            <text class="suggestion-text">{{ suggestion }}</text>
          </view>
        </view>
      </view>

      <!-- 没有搜索结果 -->
      <view v-if="searchKeyword && searchSuggestions.length === 0" class="no-results-section">
        <view class="no-results-icon">🔍</view>
        <text class="no-results-text">没有找到“{{ searchKeyword }}”的相关结果</text>
        <text class="no-results-subtext">换个关键词试试吧</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const searchKeyword = ref('')
const searchHistory = ref<string[]>([])
const hotSearchTags = ref([
  '面包',
  '蛋糕',
  '饼干',
  '甜甜圈',
  '牛角包',
  '马卡龙',
  '吐司',
  '披萨'
])
const searchSuggestions = ref<string[]>([])

// 加载搜索历史
const loadSearchHistory = () => {
  const history = uni.getStorageSync('searchHistory') || []
  searchHistory.value = history
}

// 保存搜索历史
const saveSearchHistory = () => {
  uni.setStorageSync('searchHistory', searchHistory.value)
}

// 处理搜索
const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) return

  // 添加到搜索历史（去重）
  const index = searchHistory.value.indexOf(keyword)
  if (index !== -1) {
    searchHistory.value.splice(index, 1)
  }
  searchHistory.value.unshift(keyword)
  // 限制历史记录数量
  if (searchHistory.value.length > 10) {
    searchHistory.value.pop()
  }
  saveSearchHistory()

  // 跳转到商品列表页
  uni.navigateTo({
    url: `/pages/product-list/index?keyword=${encodeURIComponent(keyword)}`
  })
}

// 处理输入
const handleInput = () => {
  const keyword = searchKeyword.value.trim()
  if (keyword) {
    // 模拟搜索建议
    searchSuggestions.value = hotSearchTags.value.filter(tag =>
      tag.includes(keyword)
    ).slice(0, 5)
  } else {
    searchSuggestions.value = []
  }
}

// 处理标签点击
const handleTagClick = (tag: string) => {
  searchKeyword.value = tag
  handleSearch()
}

// 处理历史点击
const handleHistoryClick = (item: string) => {
  searchKeyword.value = item
  handleSearch()
}

// 处理建议点击
const handleSuggestionClick = (suggestion: string) => {
  searchKeyword.value = suggestion
  handleSearch()
}

// 清空关键词
const clearKeyword = () => {
  searchKeyword.value = ''
  searchSuggestions.value = []
}

// 清空历史
const clearHistory = () => {
  uni.showModal({
    title: '提示',
    content: '确定清空搜索历史吗？',
    success: (res) => {
      if (res.confirm) {
        searchHistory.value = []
        saveSearchHistory()
      }
    }
  })
}

// 删除单个历史项
const deleteHistoryItem = (item: string) => {
  const index = searchHistory.value.indexOf(item)
  if (index !== -1) {
    searchHistory.value.splice(index, 1)
    saveSearchHistory()
  }
}

// 取消搜索
const handleCancel = () => {
  uni.navigateBack()
}

onMounted(() => {
  loadSearchHistory()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.search-page {
  padding: $spacing-md;
}

.search-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.search-input-container {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: $color-white;
  border-radius: $border-radius-lg;
  padding: $spacing-sm $spacing-md;
  border: 1px solid $color-border;
}

.search-icon {
  margin-right: $spacing-sm;
  font-size: $font-size-md;
  color: $color-text-secondary;
}

.search-input {
  flex: 1;
  font-size: $font-size-md;
  color: $color-text-primary;
  height: 40rpx;
}

.clear-icon {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-xl;
  color: $color-text-secondary;
  cursor: pointer;
}

.cancel-btn {
  padding: $spacing-sm $spacing-md;
}

.cancel-text {
  font-size: $font-size-sm;
  font-weight: 400;
  color: $color-primary;
}

.section-title {
  font-size: $font-size-md;
  font-weight: 500;
  color: $color-text-primary;
  margin-bottom: $spacing-md;
}

.hot-search-section,
.history-section,
.suggestions-section,
.no-results-section {
  margin-top: $spacing-xl;
}

.hot-search-tags {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
}

.search-tag {
  background-color: $color-white;
  border: 1px solid $color-border;
  border-radius: $border-radius-lg;
  padding: $spacing-sm $spacing-md;
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    background-color: $color-background;
  }
}

.tag-text {
  font-size: $font-size-sm;
  font-weight: 400;
  color: $color-text-primary;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.clear-history {
  font-size: $font-size-sm;
  font-weight: 300;
  color: $color-text-secondary;
  cursor: pointer;
}

.history-list {
  .history-item {
    display: flex;
    align-items: center;
    padding: $spacing-md;
    background-color: $color-white;
    border-bottom: 1px solid $color-border;
    cursor: pointer;

    &:last-child {
      border-bottom: none;
    }
  }

  .history-icon {
    margin-right: $spacing-md;
    font-size: $font-size-md;
    color: $color-text-secondary;
  }

  .history-text {
    flex: 1;
    font-size: $font-size-sm;
    font-weight: 400;
    color: $color-text-primary;
  }

  .delete-icon {
    width: 40rpx;
    height: 40rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: $font-size-xl;
    color: $color-text-secondary;
    cursor: pointer;
  }
}

.suggestions-list {
  .suggestion-item {
    display: flex;
    align-items: center;
    padding: $spacing-md;
    background-color: $color-white;
    border-bottom: 1px solid $color-border;
    cursor: pointer;

    &:last-child {
      border-bottom: none;
    }
  }

  .suggestion-icon {
    margin-right: $spacing-md;
    font-size: $font-size-md;
    color: $color-text-secondary;
  }

  .suggestion-text {
    flex: 1;
    font-size: $font-size-sm;
    font-weight: 400;
    color: $color-text-primary;
  }
}

.no-results-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl 0;
  text-align: center;

  .no-results-icon {
    font-size: 80rpx;
    margin-bottom: $spacing-md;
    color: $color-text-tertiary;
  }

  .no-results-text {
    font-size: $font-size-md;
    font-weight: 400;
    color: $color-text-primary;
    margin-bottom: $spacing-sm;
  }

  .no-results-subtext {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }
}
</style>