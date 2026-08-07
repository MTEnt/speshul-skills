export type PostKind = 'feed' | 'photo';
export type PublicationMode = 'publish_now' | 'schedule';

export interface PostDraft {
  readonly pageId: string;
  readonly kind: PostKind;
  readonly mode: PublicationMode;
  readonly message?: string;
  readonly link?: string;
  readonly photoUrl?: string;
  readonly scheduledAt?: string;
}

export interface PreparedPost {
  readonly previewId: string;
  readonly approvalPhrase: string;
  readonly contentHash: string;
  readonly createdAt: string;
  readonly expiresAt: string;
  readonly draft: PostDraft;
}

export interface FacebookPage {
  readonly id: string;
  readonly name?: string;
  readonly category?: string;
  readonly link?: string;
}

export interface FacebookPost {
  readonly id: string;
  readonly message?: string;
  readonly created_time?: string;
  readonly permalink_url?: string;
  readonly is_published?: boolean;
  readonly scheduled_publish_time?: string | number;
  readonly full_picture?: string;
}

export interface CreatedPost {
  readonly id: string;
  readonly photoId?: string;
}
