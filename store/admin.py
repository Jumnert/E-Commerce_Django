from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Address, Category, Product, Cart, Order

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    search_fields = ('locality', 'city', 'state', 'user__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'sku', 'category', 'price', 'is_active', 'is_featured', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('title', 'sku', 'short_description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__title')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id_display', 
        'user', 
        'product_name',
        'quantity', 
        'total_amount_display', 
        'payment_method',
        'payment_proof_thumbnail',
        'payment_status_badge',
        'order_status_badge',
        'quick_actions',
        'ordered_date'
    )
    
    list_filter = (
        'status', 
        'payment_method', 
        'payment_status',
        'ordered_date'
    )
    
    search_fields = (
        'id',
        'user__username',
        'user__email',
        'product__title'
    )
    
    readonly_fields = (
        'user', 
        'address', 
        'product', 
        'quantity', 
        'payment_method',
        'ordered_date',
        'payment_proof_image',
        'order_summary'
    )
    
    fieldsets = (
        ('Order Summary', {
            'fields': ('order_summary',)
        }),
        ('Order Information', {
            'fields': ('user', 'address', 'product', 'quantity', 'ordered_date')
        }),
        ('Payment Information', {
            'fields': (
                'payment_method', 
                'payment_proof_image',
                'payment_status', 
                'payment_verified_at',
                'admin_notes'
            ),
            'classes': ('wide',)
        }),
        ('Order Status', {
            'fields': ('status',)
        }),
    )
    
    actions = [
        'verify_payment', 
        'reject_payment',
        'accept_order',
        'mark_as_packed',
        'mark_as_shipped',
        'mark_as_delivered',
        'cancel_order'
    ]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/verify-payment/', self.admin_site.admin_view(self.verify_payment_view), name='order-verify-payment'),
            path('<int:order_id>/reject-payment/', self.admin_site.admin_view(self.reject_payment_view), name='order-reject-payment'),
            path('<int:order_id>/accept-order/', self.admin_site.admin_view(self.accept_order_view), name='order-accept'),
            path('<int:order_id>/update-status/<str:new_status>/', self.admin_site.admin_view(self.update_status_view), name='order-update-status'),
        ]
        return custom_urls + urls
    
    def verify_payment_view(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order.payment_status = 'Verified'
        order.payment_verified_at = timezone.now()
        order.save()
        messages.success(request, f'Payment for Order #{order_id} has been verified. ✓')
        return redirect('admin:store_order_changelist')
    
    def reject_payment_view(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order.payment_status = 'Rejected'
        order.save()
        messages.warning(request, f'Payment for Order #{order_id} has been rejected. ✗')
        return redirect('admin:store_order_changelist')
    
    def accept_order_view(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order.status = 'Accepted'
        order.save()
        messages.success(request, f'Order #{order_id} has been accepted. ✓')
        return redirect('admin:store_order_changelist')
    
    def update_status_view(self, request, order_id, new_status):
        order = Order.objects.get(pk=order_id)
        order.status = new_status
        order.save()
        messages.success(request, f'Order #{order_id} status updated to {new_status}. ✓')
        return redirect('admin:store_order_changelist')
    
    # Custom display methods
    def order_id_display(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    order_id_display.short_description = 'Order ID'
    order_id_display.admin_order_field = 'id'
    
    def product_name(self, obj):
        return obj.product.title
    product_name.short_description = 'Product'
    product_name.admin_order_field = 'product__title'
    
    def total_amount_display(self, obj):
        return format_html('<strong>${}</strong>', obj.total_amount)
    total_amount_display.short_description = 'Total'
    
    def payment_status_badge(self, obj):
        if obj.payment_method == 'COD':
            return format_html(
                '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
                '#6c757d',
                'N/A (COD)'
            )
        
        colors = {
            'Pending': '#ffc107',
            'Verified': '#28a745',
            'Rejected': '#dc3545'
        }
        icons = {
            'Pending': '⏳',
            'Verified': '✓',
            'Rejected': '✗'
        }
        color = colors.get(obj.payment_status, '#6c757d')
        icon = icons.get(obj.payment_status, '?')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 3px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.payment_status
        )
    payment_status_badge.short_description = 'Payment Status'
    payment_status_badge.admin_order_field = 'payment_status'
    
    def order_status_badge(self, obj):
        colors = {
            'Pending': '#ffc107',
            'Accepted': '#17a2b8',
            'Packed': '#007bff',
            'On The Way': '#6f42c1',
            'Delivered': '#28a745',
            'Cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.status
        )
    order_status_badge.short_description = 'Order Status'
    order_status_badge.admin_order_field = 'status'
    
    def payment_proof_thumbnail(self, obj):
        if obj.payment_proof:
            return format_html(
                '<a href="{}" target="_blank" title="Click to view full size">'
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border: 2px solid #007bff; border-radius: 4px; cursor: pointer;"/>'
                '</a>',
                obj.payment_proof.url,
                obj.payment_proof.url
            )
        return format_html('<span style="color: {};">{}</span>', '#999', '—')
    payment_proof_thumbnail.short_description = 'Payment Proof'
    
    def quick_actions(self, obj):
        actions_html = '<div style="display: flex; gap: 5px; flex-wrap: wrap;">'
        
        # Payment Actions (for QR payments only)
        if obj.payment_method == 'QR':
            if obj.payment_status == 'Pending':
                actions_html += format_html(
                    '<a href="{}" class="button" style="background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none; font-size: 11px;">✓ Verify</a>',
                    f'/admin/store/order/{obj.id}/verify-payment/'
                )
                actions_html += format_html(
                    '<a href="{}" class="button" style="background: #dc3545; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none; font-size: 11px;">✗ Reject</a>',
                    f'/admin/store/order/{obj.id}/reject-payment/'
                )
        
        # Order Status Actions
        if obj.status == 'Pending':
            actions_html += format_html(
                '<a href="{}" class="button" style="background: #17a2b8; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none; font-size: 11px;">Accept</a>',
                f'/admin/store/order/{obj.id}/accept-order/'
            )
        elif obj.status == 'Accepted':
            actions_html += format_html(
                '<a href="{}" class="button" style="background: #007bff; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none; font-size: 11px;">📦 Pack</a>',
                f'/admin/store/order/{obj.id}/update-status/Packed/'
            )
        elif obj.status == 'Packed':
            actions_html += format_html(
                '<a href="{}" class="button" style="background: #6f42c1; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none; font-size: 11px;">🚚 Ship</a>',
                f'/admin/store/order/{obj.id}/update-status/On%20The%20Way/'
            )
        elif obj.status == 'On The Way':
            actions_html += format_html(
                '<a href="{}" class="button" style="background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none; font-size: 11px;">✓ Deliver</a>',
                f'/admin/store/order/{obj.id}/update-status/Delivered/'
            )
        
        actions_html += '</div>'
        return mark_safe(actions_html)
    quick_actions.short_description = 'Quick Actions'
    
    def payment_proof_image(self, obj):
        if obj.payment_proof:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 500px; max-height: 600px; border: 3px solid #007bff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"/>'
                '</a>'
                '<br/><br/>'
                '<a href="{}" target="_blank" class="button" style="margin-top: 10px;">Open in New Tab</a>'
                '</div>',
                obj.payment_proof.url,
                obj.payment_proof.url,
                obj.payment_proof.url
            )
        return format_html('<p style="color: {}; font-style: italic;">{}</p>', '#999', 'No payment proof uploaded')
    payment_proof_image.short_description = 'Payment Proof Screenshot'
    
    def order_summary(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff;">'
            '<h3 style="margin-top: 0; color: #007bff;">Order #{}</h3>'
            '<table style="width: 100%; border-collapse: collapse;">'
            '<tr><td style="padding: 8px; font-weight: bold; width: 150px;">Customer:</td><td style="padding: 8px;">{}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: bold;">Email:</td><td style="padding: 8px;">{}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: bold;">Product:</td><td style="padding: 8px;">{}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: bold;">Quantity:</td><td style="padding: 8px;">{}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: bold;">Unit Price:</td><td style="padding: 8px;">${}</td></tr>'
            '<tr><td style="padding: 8px; font-weight: bold;">Total Amount:</td><td style="padding: 8px; font-size: 18px; color: #28a745;"><strong>${}</strong></td></tr>'
            '<tr><td style="padding: 8px; font-weight: bold;">Shipping Address:</td><td style="padding: 8px;">{}, {}, {}</td></tr>'
            '</table>'
            '</div>',
            obj.id,
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
            obj.product.title,
            obj.quantity,
            obj.product.price,
            obj.total_amount,
            obj.address.locality,
            obj.address.city,
            obj.address.state
        )
    order_summary.short_description = 'Order Details'
    
    # Bulk actions
    def verify_payment(self, request, queryset):
        updated = queryset.filter(payment_method='QR', payment_status='Pending').update(
            payment_status='Verified',
            payment_verified_at=timezone.now()
        )
        self.message_user(
            request, 
            f'{updated} payment(s) verified successfully. ✓',
            level=messages.SUCCESS
        )
    verify_payment.short_description = '✓ Verify Payment (QR only)'
    
    def reject_payment(self, request, queryset):
        updated = queryset.filter(payment_method='QR').update(
            payment_status='Rejected'
        )
        self.message_user(
            request, 
            f'{updated} payment(s) rejected. ✗',
            level=messages.WARNING
        )
    reject_payment.short_description = '✗ Reject Payment'
    
    # Order status actions
    def accept_order(self, request, queryset):
        updated = queryset.filter(status='Pending').update(status='Accepted')
        self.message_user(request, f'{updated} order(s) accepted. ✓', level=messages.SUCCESS)
    accept_order.short_description = '✓ Accept Order'
    
    def mark_as_packed(self, request, queryset):
        updated = queryset.update(status='Packed')
        self.message_user(request, f'{updated} order(s) marked as packed. 📦', level=messages.SUCCESS)
    mark_as_packed.short_description = '📦 Mark as Packed'
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='On The Way')
        self.message_user(request, f'{updated} order(s) marked as shipped. 🚚', level=messages.SUCCESS)
    mark_as_shipped.short_description = '🚚 Mark as Shipped'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='Delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered. ✓', level=messages.SUCCESS)
    mark_as_delivered.short_description = '✓ Mark as Delivered'
    
    def cancel_order(self, request, queryset):
        updated = queryset.update(status='Cancelled')
        self.message_user(request, f'{updated} order(s) cancelled. ✗', level=messages.WARNING)
    cancel_order.short_description = '✗ Cancel Order'