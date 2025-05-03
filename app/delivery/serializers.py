"""
Serializers for the delivery API View.
"""

from rest_framework import serializers

from delivery.models import DeliveryRequest
from prescriptions.models import PrescriptionRecord

from .models import Address


class DeliveryRequestSerializer(serializers.ModelSerializer):
    """Serializer for the Delivery object."""

    class Meta:
        model = DeliveryRequest
        fields = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        """Create and return a record."""
        request = self.context.get("request")
        user = request.user if request else None
        if user.is_authenticated:
            return DeliveryRequest.objects.create(**validated_data)
        else:
            raise serializers.ValidationError(
                "You do not have permission to make a delivery request."
            )

    def update(self, instance, validated_data):
        """Update and return a record."""
        request = self.context.get("request")
        user = request.user if request else None
        if user.is_authenticated:
            instance.status = validated_data.get("status", instance.status)
            if (instance.status == "delivered"):
                # update prescription status to completed
                PrescriptionRecord.objects.filter(
                    id=instance.prescription.id
                ).update(prescription_status="completed")
            instance.delivery_date = validated_data.get(
                "delivery_date", instance.delivery_date
            )
            instance.delivery_time = validated_data.get(
                "delivery_time", instance.delivery_time
            )
            instance.notes = validated_data.get("notes", instance.notes)
            instance.cost = validated_data.get("cost", instance.cost)
            instance.delivery_person = validated_data.get(
                "delivery_person", instance.delivery_person
            )
            instance.delivery_address = validated_data.get(
                "destination_address", instance.delivery_address
            )
            instance.prescription = validated_data.get(
                "prescription", instance.prescription
            )
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                "You do not have permission to update a record."
            )


class AddressSerializer(serializers.ModelSerializer):
    """
    Handles create / update of Address instances.
    On first address creation we silently set it as default if none exists.
    """

    class Meta:
        model = Address
        fields = [
            "id",
            "city",
            "area",
            "building",
            "notes",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user

        # If user has no addresses yet, make first one default automatically.
        if not Address.objects.filter(user=user).exists():
            validated_data.setdefault("is_default", True)

        validated_data["user"] = user
        return super().create(validated_data)

    def validate(self, attrs):
        """
        Optional guard: forbid unsetting ALL defaults
        (i.e. ensure one address stays default).
        """
        if not attrs.get("is_default", False):
            instance = getattr(self, "instance", None)
            user = self.context["request"].user
            # If update would clear the only default, block it.
            if instance and instance.is_default:
                other_default = (
                    Address.objects.filter(user=user, is_default=True)
                    .exclude(pk=instance.pk)
                    .exists()
                )
                if not other_default:
                    raise serializers.ValidationError(
                        {"is_default": "At least one address must remain default."}
                    )
        return attrs
