;;; Convert s-expression publication struct to toml format.

#lang racket

(require toml)

(define publication-filename (make-parameter "publication.rkt"))
(struct publication (schema rows) #:prefab)
(define (read-publications) (call-with-input-file (publication-filename) read))

;; Read in the publications database and construct 
;; a plain alist from each publication data.
;; Alist items are in the form (schema-heading . value)

(define (publications->alists)
 (let ((mydata (read-publications)))
   (map (lambda (row)
          (map (lambda (head item)
                 (cons (second head) item))
               (publication-schema mydata)
               (vector->list row)))
        (publication-rows mydata))))

;; Publications are now in a list of alists.
;; We want to extract the "code" and use that 
;; as a hasheq key. The value for this key
;; is another hasheq initialised with the rest 
;; of the alist pairs (with the code pair removed.

(define (build-publications-hasheq alists)
 (let ((big-ht (make-hasheq)))
   (for-each 
    (lambda (alist)
     (let ((code-pair (assoc 'code alist)))
         (hash-set! big-ht 
                    (string->symbol (cdr code-pair))
                    (let ((ht (make-hasheq)))
                             (for-each (lambda (u)
                                        (hash-set! ht (car u) (cdr u)))
                                        (remq code-pair alist))
                             ht))))
               alists)
   big-ht))

;; Write the big-ht hash table to file.
;; Luckily racket's toml writer seems to always
;; do it in alphabetical order.

(define out (open-output-file "publication.toml" #:exists 'truncate))
(display (tomlexpr->string
          (build-publications-hasheq (publications->alists)))
          out)
(close-output-port out)


